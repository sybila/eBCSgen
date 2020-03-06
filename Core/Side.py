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
        return " + ".join(list(map(lambda item: "{} {}".format(item[1], item[0]), sorted(self.to_counter().items()))))

    def __lt__(self, other):
        return str(self) < str(other)

    def __len__(self):
        return len(self.agents)

    def to_list_of_strings(self):
        return list(map(str, self.agents))

    def to_counter(self):
        return collections.Counter(self.agents)

    def to_vector(self, ordering: tuple) -> State:
        """
        Convert the Side to a State accoring to given ordering.

        :param ordering: sequence of complex agents
        :return: State representing vector
        """
        vector = np.zeros(len(ordering))
        multiset = self.to_counter()
        for agent in list(multiset):
            vector[ordering.index(agent)] = multiset[agent]
        return State(vector)

    def compatible(self, other: 'Side') -> bool:
        """
        Checks whether two Sides are compatible.

        Is True only of on corresponding positions the Complexes are compatible
        and length of the Sides is equal.

        :param other: given Side
        :return: True if they are compatible
        """
        if len(self) != len(other):
            return False
        return all([self.agents[i].compatible(other.agents[i]) for i in range(len(self))])
