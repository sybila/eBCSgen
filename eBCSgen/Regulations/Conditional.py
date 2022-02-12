from eBCSgen.Regulations.Base import BaseRegulation


class Conditional(BaseRegulation):
    """
    Regulation defined as a forbidden context for every rule.
    """
    def __init__(self, regulation):
        super().__init__(regulation)
        self.memory = 0

    def __str__(self):
        return "Conditional: " + str(self.regulation)

    def __repr__(self):
        # TODO
        return "type conditional\n" + ",".join(self.regulation)

    def filter(self, current_state, candidates):
        agents = set(current_state.content.value)
        return {rule: values for rule, values in candidates.items() if not self.check_intersection(rule.label, agents)}

    def check_intersection(self, label, agents):
        if label not in self.regulation:
            return False
        return self.regulation[label] & agents


class VectorConditional(Conditional):
    def __init__(self, regulation):
        super().__init__(regulation)
        self.memory = 0

    def filter(self, current_state, candidates):
        seq = current_state
        return {rule: values for rule, values in candidates.items() if not self.check_intersection(rule.label, seq)}

    def check_intersection(self, label, agents):
        if label not in self.regulation:
            return False
        return self.regulation[label].check_intersection(agents)
