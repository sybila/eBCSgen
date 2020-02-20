from TS.Edge import Edge


class TransitionSystem:
    def __init__(self, ordering):
        self.states_encoding = dict()  # State -> int
        self.edges = set()  # Edge objects: (int from, int to, probability), can be used for explicit Storm format
        self.ordering = ordering  # used to decode State to actual agents

    def __eq__(self, other):
        # has to be done regardless the particular encoding (i.e. check isomorphism)
        # maybe some canonical encoding would come handy
        pass

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
            length = len(self.states_encoding) + 1
            self.states_encoding[state] = length
        return length

    def add_edge(self, source, target, probability):
        self.edges.add(Edge(self.states_encoding[source],
                            self.states_encoding[target],
                            probability))

    def save_to_file(self, output_file):
        pass