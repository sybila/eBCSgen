import collections


def convert_side(side):
    return list(map(lambda item: "{} {}".format(item[0], item[1]), side.items()))


class Reaction:
    def __init__(self, lhs: collections.Counter, rhs: collections.Counter, rate: str):
        """
        Class to represent BCSL rule

        :param lhs: multiset of left-hand side representing substrates
        :param rhs: multiset of left-hand side representing products
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
        return str(self.lhs) + " => " + str(self.rhs) + " @ " + self.rate

    def __lt__(self, other):
        return str(self) < str(other)
