from sortedcontainers import SortedList

from Core import Rate
from Core.Side import Side
from TS.VectorReaction import VectorReaction


class Reaction:
    def __init__(self, lhs: Side, rhs: Side, rate: Rate):
        """
        Class to represent BCSL reaction

        :param lhs: left-hand Side representing substrates
        :param rhs: left-hand Side representing products
        :param rate: string representing expression (TBA shouldn't be string !!!)
        """
        self.lhs = lhs
        self.rhs = rhs
        self.rate = rate

    def __eq__(self, other: 'Reaction'):
        return self.lhs == other.lhs and self.rhs == other.rhs and self.rate == other.rate

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.lhs) + " => " + str(self.rhs) + " @ " + str(self.rate)

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash((self.lhs, self.rhs, self.rate))

    def to_vector(self, ordering: SortedList, definitions: dict) -> VectorReaction:
        """
        Creates vector representation of the Reaction.

        :param ordering: given fixed order of unique Complexes
        :param definitions: dict of (param_name, value)
        :return: VectorReaction representation of Reaction
        """
        # if self.rate is not None:
        #     self.rate.vectorize(ordering, definitions)
        return VectorReaction(self.lhs.to_vector(ordering),
                              self.rhs.to_vector(ordering),
                              self.rate)

    def compatible(self, other: 'Reaction') -> bool:
        """
        Checks whether Reaction is compatible (position-wise) with the other Reaction.

        :param other: given Reaction
        :return: True if compatible
        """
        return self.lhs.compatible(other.lhs) and self.rhs.compatible(other.rhs)

    def create_all_compatible(self, atomic_signature: dict, structure_signature: dict):
        """
        Creates all fully specified complexes for all both Sides

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: set of all created Complexes
        """
        return set.union(*[self.lhs.create_all_compatible(atomic_signature, structure_signature) |
                           self.rhs.create_all_compatible(atomic_signature, structure_signature)])
