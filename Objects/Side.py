import collections
import numpy as np
from TS.State import State


class Side:
    def __init__(self, agents: list):
        """
        Class to represent BCSL rule

        :param agents: list of agents
        """
        self.agents = agents

    def __eq__(self, other: 'Side'):
        return self.to_counter() == other.to_counter()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return " + ".join(list(map(lambda item: "{} {}".format(item[0], item[1]), sorted(self.to_counter().items()))))

    def __lt__(self, other):
        return str(self) < str(other)

    def to_list_of_strings(self):
        return list(map(str, self.agents))

    def to_counter(self):
        return collections.Counter(self.agents)

    def to_vector(self, ordering: tuple) -> State:
        vector = np.zeros(len(ordering))
        multiset = self.to_counter()
        for agent in list(multiset):
            vector[ordering.index(agent)] = multiset[agent]
        return State(vector)
