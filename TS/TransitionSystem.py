from TS.Edge import Edge
from TS.State import State


class TransitionSystem:
    def __init__(self, ordering: tuple):
        self.states_encoding = dict()  # State -> int
        self.edges = set()  # Edge objects: (int from, int to, probability), can be used for explicit Storm format
        self.ordering = ordering  # used to decode State to actual agents

    def __eq__(self, other: 'TransitionSystem'):
        """
        Compares with another TransitionSystem regardless the particular encoding (i.e. check isomorphism).

        ! a different ordering could be also considered during comparision !

        :param other: given TransitionSystem
        :return: True if equal
        """
        recoded_ts = self.recode(other.states_encoding)
        return recoded_ts.edges == other.edges and self.ordering == other.ordering

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

    def add_edge(self, source: State, target: State, probability: float) -> Edge:
        """
        Added a new edge with code representations of given States.

        :param source: origin state
        :param target: target state
        :param probability: probability of transition
        :return: created Edge
        """
        edge = Edge(self.states_encoding[source],
                    self.states_encoding[target],
                    probability)
        self.edges.add(edge)
        return edge

    def recode(self, new_encoding: dict) -> 'TransitionSystem':
        """
        Recodes the transition system according to the new encoding.

        :param new_encoding: given new encoding
        :return: new TransitionSystem
        """
        ts = TransitionSystem(self.ordering)
        ts.states_encoding = new_encoding

        # swap dictionary
        old_encoding = {value: key for key, value in self.states_encoding.items()}
        ts.edges = set(map(lambda edge: edge.recode(old_encoding, new_encoding), self.edges))
        return ts

    def save_to_json(self, output_file):
        pass
