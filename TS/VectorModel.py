from TS.State import State


class VectorModel:
    def __init__(self, vector_reactions: set, init: State):
        self.vector_reactions = vector_reactions
        self.init = init

    def __eq__(self, other: 'VectorModel') -> bool:
        return self.vector_reactions == other.vector_reactions and self.init == other.init

    def generate_TS(self) -> State:
        pass

    def simulate(self, options) -> list:
        pass
