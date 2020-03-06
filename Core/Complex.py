import collections
import itertools


class Complex:
    def __init__(self, agents: list, compartment: str):
        self.agents = agents
        self.compartment = compartment

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ".".join(list(map(str, self.agents))) + "::" + self.compartment

    def __lt__(self, other: 'Complex'):
        return str(self) < str(other)

    def __eq__(self, other: 'Complex'):
        return self.compartment == other.compartment and\
               collections.Counter(self.agents) == collections.Counter(other.agents)

    def __hash__(self):
        return hash(str(self))

    def extend_signature(self, atomic_signature: dict, structure_signature: dict):
        """
        Extend given signatures by possibly new context.

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: updated signatures
        """
        for agent in self.agents:
            atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
        return atomic_signature, structure_signature

    def compatible(self, other: 'Complex'):
        """
        Checks whether two Complexes are compatible.

        :param other: another Complex
        :return: True if they are compatible
        """
        if type(self) != type(other):
            return False
        if self == other:
            return True
        self_agents = collections.Counter(self.agents)
        other_agents = collections.Counter(other.agents)
        if self.compartment == other.compartment and sum(self_agents.values()) == sum(other_agents.values()):
            other_permutations = list(itertools.permutations(list(other_agents.elements())))
            for self_perm in itertools.permutations(list(self_agents.elements())):
                for other_perm in other_permutations:
                    if all([self_perm[i].compatible(other_perm[i]) for i in range(len(self_perm))]):
                        return True
        return False
