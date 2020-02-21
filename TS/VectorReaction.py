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

    def apply(self, state: State, bound: float):
        """
        Applies the reaction on a given State.

        First, source is subtracted from the given State, then it is checked if all
        values are greater then 0. If so, new State is create as sum with target
        and rate is evaluated. Moreover, it is possible that the resulting state is greater
        than allowed bound, then infinite State is returned instead.

        :param state: given State
        :param bound: allow bound on particular values
        :return: new State and evaluated rate
        """
        new_state = state - self.source
        if new_state.check_negative():
            return new_state.add_with_bound(self.target, bound), self.rate.evaluate(state)
        return None, None

    def to_symbolic(self):
        """
        Transforms rate of the reaction to symbolic representation (used in ODEs).
        """
        self.rate.to_symbolic()
