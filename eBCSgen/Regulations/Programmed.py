from eBCSgen.Errors.RegulationParsingError import RegulationParsingError
from eBCSgen.Regulations.Base import BaseRegulation


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
        if len(current_state.memory.history) == 0:
            return candidates
        last_rule = current_state.memory.history[-1]
        if last_rule in self.regulation:
            return {rule: values for rule, values in candidates.items() if rule.label in self.regulation[last_rule]}
        return candidates
    
    def check_labels(self, model_labels):
        for rule_label, successors_labels in self.regulation.items():
            if rule_label not in model_labels:
                raise RegulationParsingError(f"Label {rule_label} in programmed regulation not present in model")
            if not successors_labels.issubset(model_labels):
                missing_labels = successors_labels - model_labels
                raise RegulationParsingError(f"Label(s) {missing_labels} in programmed regulation not present in model")
        return True