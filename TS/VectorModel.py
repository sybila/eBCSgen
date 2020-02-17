from TS.State import State


class VectorModel:
    def __init__(self, vector_reactions: set, init: State, ordering: tuple, bound: int):
        self.vector_reactions = vector_reactions
        self.init = init
        self.ordering = ordering
        self.bound = bound if bound else self.compute_bound()

    def __eq__(self, other: 'VectorModel') -> bool:
        return self.vector_reactions == other.vector_reactions and\
               self.init == other.init and self.ordering == other.ordering

    def __str__(self):
        return "Vector model:\n" + "\n".join(map(str, sorted(self.vector_reactions))) + "\n\n" \
               + str(self.init) + "\n\n" + str(self.ordering)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def compute_bound(self):
        reation_max = max(map(lambda r: max(max(r.source.sequence), max(r.target.sequence)), self.vector_reactions))
        return max(reation_max, max(self.init.sequence))

    def generate_transition_system(self) -> State:
        # reaction vectors have already replaced known parameters by their values
        # should be done in parallel
        pass

    def deterministic_simulation(self, options) -> list:
        # generate ODEs
        pass

    def stochastic_simulation(self, options) -> list:
        # Gillespie algorithm
        pass
