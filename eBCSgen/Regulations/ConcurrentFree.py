from eBCSgen.Errors.RegulationParsingError import RegulationParsingError
from eBCSgen.Regulations.Base import BaseRegulation


class ConcurrentFree(BaseRegulation):
    """
    Regulation defined as a priority function assigning priority to more important rule.
    """
    def __init__(self, regulation):
        super().__init__(regulation)
        self.memory = 0

    def __str__(self):
        return "Concurrent-free: " + str(self.regulation)

    def __repr__(self):
        return "type concurrent-free\n" + ",".join(self.regulation)

    def filter(self, current_state, candidates):
        for (p_rule_label, non_p_rule_label) in self.regulation:
            p_rule = {rule for rule in candidates if rule.label == p_rule_label}
            non_p_rule = {rule for rule in candidates if rule.label == non_p_rule_label}
            if p_rule and non_p_rule:
                del candidates[non_p_rule.pop()]
        return candidates

    def check_labels(self, model_labels):
        for tuple in self.regulation:
            for label in tuple:
                if label not in model_labels:
                    raise RegulationParsingError(f"Label {label} in concurrent-free regulation not present in model")
        return True