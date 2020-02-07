from Objects import Rate
from Objects.Side import Side
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
        return hash(str(self))

    def to_vector(self, ordering: tuple) -> VectorReaction:
        self.rate.vectorize(ordering)
        return VectorReaction(self.lhs.to_vector(ordering),
                              self.rhs.to_vector(ordering),
                              self.rate)
