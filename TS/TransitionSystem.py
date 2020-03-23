import json
import numpy as np
from itertools import groupby

from TS.Edge import Edge
from TS.State import State


class TransitionSystem:
    def __init__(self, ordering: tuple):
        self.states_encoding = dict()  # State -> int
        self.edges = set()  # Edge objects: (int from, int to, probability), can be used for explicit Storm format
        self.ordering = ordering  # used to decode State to actual agents
        self.init = int

        # for TS generating
        self.unprocessed = set()
        self.processed = set()

    def __str__(self):
        return str(self.states_encoding) + "\n" + "\n".join(list(map(str, self.edges))) + "\n" + str(self.ordering)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        """
        Used to iterate over equivalence classes (given by source) of sorted edges.
        """
        self.index = 0
        edges = sorted(self.edges)
        self.data = groupby(edges, key=lambda edge: edge.source)
        return self

    def __next__(self):
        new = next(self.data)
        return list(new[-1])

    def __eq__(self, other: 'TransitionSystem'):
        """
        Compares with another TransitionSystem regardless the particular encoding (i.e. check isomorphism).

        :param other: given TransitionSystem
        :return: True if equal
        """
        success, reordering_indices = create_indices(other.ordering, self.ordering)
        if not success:  # the agents in orderings are different => also whole TSs are different
            return False

        re_encoding = {key.reorder(reordering_indices): self.states_encoding[key] for key in self.states_encoding}

        # new TransitionSystem with ordering taken from other and reordered states in re_encoding
        ts = TransitionSystem(other.ordering)
        ts.states_encoding = re_encoding
        ts.edges = self.edges

        try:
            ts.recode(other.states_encoding)
        except KeyError:
            return False

        # this is weird, but well...
        return set(map(hash, ts.edges)) == set(map(hash, other.edges))
        # return ts.edges == other.edges

    def encode(self, init: State):
        """
        Assigns a unique code to each State for storing purposes
        """
        for state in self.processed | self.unprocessed:
            if state not in self.states_encoding:
                self.states_encoding[state] = len(self.states_encoding) + 1

        self.init = self.states_encoding[init]
        self.processed = set()
        self.encode_edges()

    def encode_edges(self):
        """
        Encodes every State in Edge according to the unique encoding.
        """
        for edge in self.edges:
            edge.encode(self.states_encoding)

    def create_decoding(self) -> dict:
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
        # swap dictionary
        old_encoding = self.create_decoding()
        self.edges = set(map(lambda edge: edge.recode(old_encoding, new_encoding), self.edges))

    def save_to_json(self, output_file: str):
        """
        Save current TS as a JSON file.

        :param output_file: given file to write to
        """
        nodes = {value: str(key) for key, value in self.states_encoding.items()}
        unique = list(map(str, self.ordering))
        edges = [edge.to_dict() for edge in self.edges]

        data = {'nodes': nodes, 'edges': edges, 'ordering': unique}

        if self.unprocessed:
            data['unprocessed'] = [str(state) for state in self.unprocessed]

        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def change_hell(self, bound):
        """
        Changes hell from inf to bound + 1.

        TODO: maybe we could get rid of inf completely, by it is more clear for
        debugging purposes

        :param bound: given allowed bound
        """
        for key, value in self.states_encoding.items():
            if key.is_inf:
                del self.states_encoding[key]
                hell = State(np.array([bound + 1] * len(key)))
                hell.is_inf = True
                self.states_encoding[hell] = value
                break

    # nemozu byt stavy, ktore nemaju odchadzajuce hrany
    def save_to_STORM_explicit(self, output_transitions, output_labels):

        def has_outgoing_edges(state):
            for edge in self.edges:
                if edge.source == state: return True
            return False

        trans_file = open(output_transitions, "w+")
        trans_file.write("dtmc\n")
        for key, value in self.states_encoding.items():
            if not has_outgoing_edges(value):
                # !!! adding edge to existing TS
                self.edges.add(Edge(value, value, 1))

        for edge in self.order_edges_source():
            trans_file.write(str(edge) + "\n")
        trans_file.close()

        label_file = open(output_labels, "w+")
        label_file.write("#DECLARATION\ninit ")
        # for agent in self.ordering:
        #    label_file.write(str(agent) + " ")
        label_file.write("deadlock\n#END\n0 init\n")
        for state in self.states_encoding:
            if state.is_hell():
                print(state)
                label_file.write(str(state.sequence) + "deadlock")
        label_file.close()

    def save_to_prism(self, output_prism, bound):
        """
        create prism file, DTMC representation of the bcs model

        TODO
        bound not correct?
        unique variables generator
        undefined parameters from rates
        without space at the end of the line
        """

        def code_transitions():
            body = ""
            if len(self.edges):
                orderd_edges = sorted(self.edges)
                print(orderd_edges)
                print(self.states_encoding)
                previous = None
                for edge in orderd_edges:

                    if self.decode_state(edge.source).is_hell():
                        continue
                    elif previous is None or previous.source != edge.source:
                        #
                        # from
                        body += "\t[] " + stateToString(self.decode_state(edge.source).sequence) + " ->"
                        # to
                        body += " " + str(edge.probability) + " : " + stateToString(
                            self.decode_state(edge.target).sequence, True) + ";\n"

                    else:
                        if body:
                            body = body[:-2]
                            body += " +"
                        body += " " + str(edge.probability) + " : " + stateToString(
                            self.decode_state(edge.target).sequence, True) + ";\n"
                    previous = edge
            return body

        prism_file = open(output_prism, "w+")
        prism_file.write("dtmc\n\n")
        # constants = create_const(self.definitions)
        prism_file.write("\n\nmodule bcs\n")
        iterator = 0
        for elem in self.decode_state(0).sequence:
            prism_file.write("\t" + "n" + str(iterator) + " : [0.." \
                             + str(bound) + "] init " + str(elem) + ";" \
                             + " // " + str(self.ordering[iterator]) + "\n")

        prism_file.write("\n" + code_transitions() + "\nendmodule\n")
        prism_file.close()

    def edges_to_PRISM(self):
        decoding = self.create_decoding()
        for group in self:
            print(group)


def create_indices(ordering_1: tuple, ordering_2: tuple):
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


def take_source(edge):
    return edge.source
