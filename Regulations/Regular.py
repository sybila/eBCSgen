import regex

from Regulations.Base import BaseRegulation


class Regular(BaseRegulation):
    """
    Regulation defined as omega-regular expression (actually not omega for now).
    """
    def __init__(self, regulation):
        super(Regular, self).__init__(regulation)
        self.regulation = regex.compile(regulation)
        self.memory = 2

    def filter(self, current_state, candidates):
        path = "".join(current_state.used_rules)
        return {rule: values for rule, values in candidates.items()
                if self.regulation.fullmatch(path + rule.label, partial=True) is not None}
