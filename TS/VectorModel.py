from TS.State import State


class VectorModel:
    def __init__(self, vector_reactions: set, init: State, bound: int):
        self.vector_reactions = vector_reactions
        self.init = init
        self.bound = bound if bound else self.compute_bound()

    def __eq__(self, other: 'VectorModel') -> bool:
        return self.vector_reactions == other.vector_reactions and self.init == other.init

    def compute_bound(self):
        # visit all reactions and inits
        pass

    def generate_TS(self) -> State:
        # sympy.sympify(s).subs([('v', 5)]) can be used on evaluated rate to obtain evaluation by parameters
        pass

    def simulate(self, options) -> list:
        pass
