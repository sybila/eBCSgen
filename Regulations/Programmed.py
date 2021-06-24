from Regulations.Base import BaseRegulation


class Programmed(BaseRegulation):
    """
    Regulation defined as successor function for every rule.
    Only set of successor rules is allowed to be used in the next step.
    """
    def __init__(self, regulation):
        super().__init__(regulation)
        self.memory = 1

    def __str__(self):
        return "Successors: " + str(self.regulation)

    def __repr__(self):
        # TODO
        return "type programmed\n" + str(self.regulation)

    def filter(self, current_state, candidates):
        if len(current_state.used_rules) == 0:
            return candidates
        last_rule = current_state.used_rules[-1]
        return {rule: values for rule, values in candidates.items() if rule.label in self.regulation[last_rule]}
