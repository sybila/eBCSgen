import json
import numpy as np

from TS.Edge import Edge
from TS.State import State


class TransitionSystem:
    def __init__(self, ordering: tuple):
        self.states_encoding = dict()  # State -> int
        self.edges = set()  # Edge objects: (int from, int to, probability), can be used for explicit Storm format
        self.ordering = ordering  # used to decode State to actual agents

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

        return ts.edges == other.edges

    def get_state_encoding(self, state: 'State') -> int:
        """
        Returns code of particular State if already exists,
        otherwise it is created and returned.

        :param state: given State to be checked
        :return: the code of the State
        """
        if state in self.states_encoding:
            return self.states_encoding[state]
        else:
            length = len(self.states_encoding)
            self.states_encoding[state] = length
        return length

    def new_edge(self, source: State, target: State, probability: float) -> Edge:
        """
        Added a new edge with code representations of given States.

        :param source: origin state
        :param target: target state
        :param probability: probability of transition
        :return: created Edge
        """
        edge = Edge(self.get_state_encoding(source),
                    self.get_state_encoding(target),
                    probability)
        return edge

    def recode(self, new_encoding: dict):
        """
        Recodes the transition system according to the new encoding.

        :param new_encoding: given new encoding
        :return: new TransitionSystem
        """
        # swap dictionary
        old_encoding = {value: key for key, value in self.states_encoding.items()}
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

        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def save_to_PRISM_explicit(self, output_file):
        pass


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
