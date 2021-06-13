from Regulations.Base import BaseRegulation


class Conditional(BaseRegulation):
    """
    Regulation defined as a forbidden context for every rule.
    """
    def __init__(self, regulation):
        super().__init__(regulation)
        self.memory = 0

    def filter(self, current_state, candidates):
        agents = set(current_state.multiset)
        return {rule: values for rule, values in candidates.items() if not self.regulation[rule.label] & agents}
