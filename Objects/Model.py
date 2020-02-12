import collections
from TS.State import State


class Model:
    def __init__(self, rules: set, init: collections.Counter, definitions: dict, bound: int):
        self.rules = rules
        self.init = init
        self.definitions = definitions

        # autocomplete
        self.bound = bound if bound else self.compute_bound()
        # self.atomic_signature, self.structure_signature = self.extract_signatures()

    def __eq__(self, other: 'Model') -> bool:
        return self.rules == other.rules and self.init == other.init

    def extract_signatures(self):
        pass

    def compute_bound(self):
        pass

    def generate_TS(self) -> State:
        pass

    def simulate(self, options) -> list:
        pass

    def check_PCTL(self, PCTL_formula) -> bool:
        pass

    def parameter_synthesis(self, PCTL_formula) -> list:
        pass
