import collections
from TS.State import State


class Model:
    def __init__(self, rules: set, init: collections.Counter, definitions: dict, bound: int):
        self.rules = rules
        self.init = init
        self.definitions = definitions
        self.bound = bound
        self.all_rates = True

        # autocomplete
        self.atomic_signature, self.structure_signature = self.extract_signatures()

    def __eq__(self, other: 'Model') -> bool:
        return self.rules == other.rules and self.init == other.init and self.definitions == other.definitions

    def extract_signatures(self):
        """
        Automatically creates signature from context of rules and initial state.
        Additionally it checks if all rules have a rate, sets all_rates to False otherwise.

        :return: created atomic and structure signatures
        """
        atomic_signature, structure_signature = dict(), dict()
        for rule in self.rules:
            if rule.rate is None:
                self.all_rates = False
            for agent in rule.agents:
                atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
        for agent in list(self.init):
            atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
        return atomic_signature, structure_signature

    def to_vector_model(self):
        reactions = set()

        pass

    def generate_TS(self) -> State:
        pass

    def simulate(self, options) -> list:
        pass

    def check_PCTL(self, PCTL_formula) -> bool:
        pass

    def parameter_synthesis(self, PCTL_formula) -> list:
        pass
