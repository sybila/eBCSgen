from TS.State import State


class Model:
    def __init__(self, rules: set, init: State, atomic_signature: dict, structure_signature: dict):
        self.rules = rules
        self.init = init
        self.atomic_signature = atomic_signature
        self.structure_signature = structure_signature

    def __eq__(self, other: 'Model') -> bool:
        return self.rules == other.rules and self.init == other.init

    def generate_TS(self) -> State:
        pass

    def simulate(self, options) -> list:
        pass

    def check_PCTL(self, PCTL_formula) -> bool:
        pass

    def parameter_synthesis(self, PCTL_formula) -> list:
        pass
