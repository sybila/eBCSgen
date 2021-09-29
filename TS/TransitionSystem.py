import json
from copy import copy

import numpy as np
from sortedcontainers import SortedList
from pyModelChecking import Kripke

from TS.State import State, Memory, Vector


class TransitionSystem:
    def __init__(self, ordering: SortedList = None, bound=None):
        self.ordering = ordering  # used to decode State to actual agents
        self.bound = bound

        # for TS generating
        self.unprocessed = set()
        self.states = set()
        self.edges = set()

        self.states_encoding = dict()  # int -> State

        # for multiset approach
        self.unique_complexes = set()

        self.init = None
        self.params = []

    def __str__(self):
        return str(self.states_encoding) + "\n" + "\n".join(list(map(str, self.edges))) + "\n" + str(self.ordering)

    def __repr__(self):
        return str(self)

    def __eq__(self, other: 'TransitionSystem'):
        """
        Compares with another TransitionSystem regardless the particular encoding (i.e. check isomorphism).

        :param other: given TransitionSystem
        :return: True if equal
        """

        # remove possibly unused agents
        other = other.filter_unused_agents()

        success, reordering_indices = create_indices(other.ordering, self.ordering)
        if not success:  # the agents in orderings are different => also whole TSs are different
            return False

        re_encoding = {key: self.states_encoding[key].reorder(reordering_indices) for key in self.states_encoding}

        # new TransitionSystem with ordering taken from other and reordered states in re_encoding
        ts = TransitionSystem(other.ordering, other.bound)
        ts.states_encoding = re_encoding
        ts.edges = self.edges

        try:
            ts.recode(other.revert_encoding())
        except KeyError:
            return False

        return set(map(hash, ts.edges)) == set(map(hash, other.edges))

    def encode(self):
        """
        Assigns a unique code to each State for storing purposes
        """
        for state in self.states | self.unprocessed:
            if state not in self.states_encoding:
                self.states_encoding[state] = len(self.states_encoding) + 1

        if type(self.init) != int:
            self.init = self.states_encoding[self.init]

        self.encode_edges()
        # to achieve int -> State format
        self.states_encoding = self.revert_encoding()

    def encode_edges(self):
        """
        Encodes every Vector in Edge according to the unique encoding.
        """
        for edge in self.edges:
            edge.encode(self.states_encoding)

    def decode(self):
        """
        Flips encoding to continue in generating.
        """
        self.init = self.states_encoding[self.init]
        self.states_encoding = self.revert_encoding()

    def revert_encoding(self) -> dict:
        """
        Swaps encoding dictionary for decoding purposes.

        :return: swapped dictionary
        """
        return {value: key for key, value in self.states_encoding.items()}

    def recode(self, new_encoding: dict):
        """
        Recodes the transition system according to the new encoding.

        :param new_encoding: given new encoding
        :return: new TransitionSystem
        """
        self.edges = set(map(lambda edge: edge.recode(self.states_encoding, new_encoding), self.edges))

    def save_to_json(self, output_file: str, params=None):
        """
        Save current TS as a JSON file.

        :param params: given set of unknown parameters
        :param output_file: given file to write to
        """
        unique = list(map(str, self.ordering))
        edges = [edge.to_dict() for edge in self.edges]
        states = {key: str(state.content) for key, state in self.states_encoding.items()}

        data = {'nodes': states, 'edges': edges, 'ordering': unique,
                'initial': self.init, 'bound': int(self.bound)}
        if params:
            data['parameters'] = list(params)

        if self.unprocessed:
            data['unprocessed'] = [str(state.content) for state in self.unprocessed]

        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def change_hell(self):
        """
        Changes hell from inf to bound + 1.
        """
        for key, value in self.states_encoding.items():
            if value.is_inf:
                del self.states_encoding[value]
                hell = State(Vector(np.array([self.bound + 1] * len(key))), Memory(0), True)
                self.states_encoding[hell] = value
                break

    def create_AP_labels(self, APs: list, include_init=True):
        """
        Creates label for each AtomicProposition.
        Moreover, goes through all states in ts.states_encoding and validates whether they satisfy given
         APs - if so, the particular label is assigned to the state.

        :param APs: give AtomicProposition extracted from Formula
        :return: dictionary of State_code -> set of labels and AP -> label
        """
        AP_lables = dict()
        for ap in APs:
            AP_lables[ap] = "property_" + str(len(AP_lables))

        state_labels = dict()
        for state in self.states_encoding.keys():
            for ap in APs:
                if state.check_AP(ap, self.ordering):
                    state_labels[self.states_encoding[state]] = \
                        state_labels.get(self.states_encoding[state], set()) | {AP_lables[ap]}
        if include_init:
            state_labels[self.init] = state_labels.get(self.init, set()) | {"init"}
        return state_labels, AP_lables

    def change_to_vector_backend(self):
        """
        Changes backend from Multisets to Vectors by encoding them.
        """
        self.ordering = SortedList(sorted(self.unique_complexes))
        self.encode()

        vector_encoding = dict()
        for key, state in self.states_encoding.items():
            state.to_vector(self.ordering)
            vector_encoding[key] = state
        self.states_encoding = vector_encoding

    def save_to_STORM_explicit(self, transitions_file: str, labels_file: str, state_labels: dict, AP_labels):
        """
        Save the TransitionSystem as explicit Storm file (no parameters).

        :param transitions_file: file for transitions
        :param labels_file: file for labels
        :param labels: labels representing atomic propositions assigned to states
        """
        trans_file = open(transitions_file, "w+")
        trans_file.write("dtmc\n")

        for edge in sorted(self.edges):
            trans_file.write(str(edge) + "\n")
        trans_file.close()

        label_file = open(labels_file, "w+")
        unique_labels = ['init'] + list(map(str, AP_labels.values()))
        label_file.write("#DECLARATION\n" + " ".join(unique_labels) + "\n#END\n")

        label_file.write("\n".join([str(state) + " " + " ".join(list(map(str, state_labels[state])))
                                    for state in sorted(state_labels)]))
        label_file.close()

    def save_to_prism(self, output_file: str, params: set, prism_formulas: list):
        """
        Save the TransitionSystem as a PRISM file (parameters present).

        :param output_file: output file name
        :param params: set of present parameters
        :param prism_formulas: definition of abstract Complexes
        """

        prism_file = open(output_file, "w+")
        prism_file.write("dtmc\n")

        # declare parameters
        prism_file.write("\n" + "\n".join(["\tconst double {};".format(param) for param in params]) + "\n")
        prism_file.write("\nmodule TS\n")

        # to get rid of inf
        self.change_hell()
        decoding = self.revert_encoding()

        # declare state variables
        init = decoding[self.init]
        vars = ['\tVAR_{} : [0..{}] init {}; // {}'.format(i, self.bound + 1, int(init.value[i]), self.ordering[i])
                for i in range(len(self.ordering))]
        prism_file.write("\n" + "\n".join(vars) + "\n")

        # write transitions
        transitions = self.edges_to_PRISM(decoding)
        prism_file.write("\n" + "\n".join(transitions))

        prism_file.write("\nendmodule\n\n")

        # write formulas
        if prism_formulas:
            prism_file.write("\n\tformula " + "\n".join(prism_formulas))

        prism_file.close()

    def edges_to_PRISM(self, decoding):
        """
        Takes ordered edges grouped by source and for each group creates PRISM file representation

        :return: list of strings for each group (source)
        """
        from itertools import groupby
        data = groupby(sorted(self.edges), key=lambda edge: edge.source)

        output = []
        for group in data:
            group = group[-1]
            source = group[0].source
            line = '\t[] {} -> '.format(decoding[source].to_PRISM_string()) + \
                   " + ".join(list(map(lambda edge: edge.to_PRISM_string(decoding), group))) + ";"
            output.append(line)
        return output

    def to_kripke(self, state_labels):
        """
        Create Kripke structure in format of pyModelChecking module.

        :return: Kripke structure representation of the transition system
        """
        states = list(self.states_encoding.keys())
        edges = [(edge.source, edge.target) for edge in self.edges]
        inits = [self.init]
        return Kripke(S=states, R=edges, S0=inits, L=state_labels)

    def filter_unused_agents(self):
        """
        There are cases when agents which are always 0 are used.
        This methods removed such agents and fixes encoding.

        :return: minimalised TS
        """
        check = Vector(np.zeros(len(list(self.states_encoding.values())[0].content)))
        for state in self.states_encoding.values():
            check += state.content

        ordering = copy(self.ordering)

        to_remove = []
        for i in range(len(check)):
            if check.value[i] == 0:
                to_remove.append(i)

        for code, state in self.states_encoding.items():
            new_sequence = np.delete(state.content.value, to_remove)
            state.content.value = new_sequence

        for i in reversed(to_remove):
            del ordering[i]

        new_ts = TransitionSystem(ordering, self.bound)
        new_ts.init = self.init
        new_ts.edges = self.edges
        new_ts.states_encoding = self.states_encoding
        return new_ts


def create_indices(ordering_1: SortedList, ordering_2: SortedList):
    """
    Creates indices np.array which represents how agents from ordering_1 have to be rearranged
    in order to fit agents from ordering_2. If such relation is not possible, return False.

    :param ordering_1: first agents ordering
    :param ordering_2: second agents ordering
    :return: np.array of indices
    """
    if set(ordering_1) == set(ordering_2):
        result = []
        for i_1 in range(len(ordering_1)):
            for i_2 in range(len(ordering_2)):
                if ordering_1[i_1] == ordering_2[i_2]:
                    result.append(i_2)
                    break
        return True, np.array(result)
    else:
        return False, None
