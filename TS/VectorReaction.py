from Core.Rate import Rate
from TS.State import State


class VectorReaction:
    def __init__(self, source: State, target: State, rate: Rate, label=None):
        self.source = source
        self.target = target
        self.rate = rate
        self.label = label

    def __str__(self):
        label = self.label + " ~ " if self.label else ""
        return label + str(self.source) + " -> " + str(self.target) + " @ " + str(self.rate)

    def __eq__(self, other: 'VectorReaction'):
        return self.source == other.source and self.target == other.target and self.rate == other.rate

    def __repr__(self):
        return str(self)

    def __lt__(self, other: 'VectorReaction'):
        return str(self) < str(other)

    def __hash__(self):
        return hash(str(self))

    def evaluate_rate(self, state, definitions):
        _ = definitions  # unused argument
        return self.rate.evaluate(state)

    def match(self, state, all=False):
        _ = all  # unused argument
        if state >= self.source:
            return [self.source.content]
        return None

    def replace(self, aligned_match):
        _ = aligned_match  # unused argument
        return self.target.content

    def reconstruct_complexes_from_match(self, match):
        # to ensure compatibility with Rule
        return match

    def to_symbolic(self):
        """
        Transforms rate of the reaction to symbolic representation (used in ODEs).
        """
        self.rate.to_symbolic()
