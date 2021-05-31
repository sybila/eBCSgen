from Regulations.Base import BaseRegulation


class ConcurrentFree(BaseRegulation):
    """
    Regulation defined as a priority function assigning priority to more important rule.
    """
    def filter(self, current_state, candidates):
        for (p_rule_label, non_p_rule_label) in self.regulation:
            p_rule = {rule for rule in candidates if rule.label == p_rule_label}
            non_p_rule = {rule for rule in candidates if rule.label == non_p_rule_label}
            if p_rule and non_p_rule:
                del candidates[non_p_rule.pop()]
        return candidates
