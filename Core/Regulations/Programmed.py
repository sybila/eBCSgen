from Core.Regulations.Base import BaseRegulation


class Programmed(BaseRegulation):
    def filter(self, current_state, candidates):
        if len(current_state.used_rules_path) == 0:
            return candidates
        last_rule = current_state.used_rules_path[-1]
        return {rule: values for rule, values in candidates.items() if rule.label in self.regulation[last_rule]}
