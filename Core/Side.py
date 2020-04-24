import collections
import numpy as np

from Core.Complex import Complex
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

    def __hash__(self):
        return hash(frozenset(self.to_counter().items()))

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
        vector = np.zeros(len(ordering), dtype=int)
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
        if len(self) > len(other):
            return False
        return all([self.agents[i].compatible(other.agents[i]) for i in range(len(self))])

    def exists_compatible_agent(self, agent: Complex) -> bool:
        """
        Checks whether there exists a compatible agent in the Side.

        :param agent: given Complex agent
        :return: True if exists compatible
        """
        return any(list(map(lambda a: a.compatible(agent), self.agents)))

    def create_all_compatible(self, atomic_signature: dict, structure_signature: dict):
        """
        Creates all fully specified complexes for all complexes in Side

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: set of all created Complexes
        """
        return set.union(*[complex.create_all_compatible(atomic_signature, structure_signature)
                           for complex in self.agents])
