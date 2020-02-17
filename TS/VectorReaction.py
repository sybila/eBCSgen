from Core.Rate import Rate
from TS.State import State


class VectorReaction:
    def __init__(self, source: State, target: State, rate: Rate):
        self.source = source
        self.target = target
        self.rate = rate

    def __str__(self):
        return str(self.source) + " -> " + str(self.target) + " @ " + str(self.rate)

    def __eq__(self, other: 'VectorReaction'):
        return self.source == other.source and self.target == other.target and self.rate == other.rate

    def __repr__(self):
        return str(self)

    def __lt__(self, other: 'VectorReaction'):
        return str(self) < str(other)

    def __hash__(self):
        return hash(str(self))

    def apply(self, state: State, bound: int):
        new_state = state - self.source
        if new_state.check_negative(bound):
            return new_state + self.target, self.rate.evaluate(state)
