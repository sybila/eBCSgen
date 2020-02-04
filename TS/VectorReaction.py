from TS.State import State


class VectorReaction:
    def __init__(self, source: State, target: State, rate: str):
        self.source = source
        self.target = target
        self.rate = rate

    def apply(self, state: State, bound: int):
        new_state = state - self.source
        if new_state.check_negative(bound):
            return new_state + self.target, self.eval_rate(state)

    def eval_rate(self, state: State) -> float:
        # do some magic with expression
        # for each vector v representing complex call
        # state.filter_values(v)
        pass
