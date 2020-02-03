import collections
from Objects.Complex import Complex


class Rule:
    def __init__(self, agents: tuple, mid: int, compartments: list, complexes: list, pairs: list, rate: str):
        self.agents = agents
        self.mid = mid
        self.compartments = compartments
        self.complexes = complexes
        self.pairs = pairs
        self.rate = rate

    def __eq__(self, other: 'Rule'):
        return self.agents == other.agents and self.mid == other.mid and self.compartments == other.compartments and \
               self.complexes == other.complexes and self.pairs == other.pairs

    def __repr__(self):
        return str(self)

    def __str__(self):
        lhs, rhs = self.create_complexes()
        lhs = list(map(str, lhs))
        rhs = list(map(str, rhs))
        return " + ".join(lhs) + " => " + " + ".join(rhs) + " @ " + self.rate

    def __lt__(self, other):
        return str(self) < str(other)

    def create_complexes(self):
        lhs, rhs = [], []
        for (f, t) in self.complexes:
            c = Complex(collections.Counter(self.agents[f:t + 1]), self.compartments[f])
            lhs.append(c) if t < self.mid else rhs.append(c)
        return lhs, rhs
