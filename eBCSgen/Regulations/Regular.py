import regex
from eBCSgen.Errors.RegulationParsingError import RegulationParsingError

from eBCSgen.Regulations.Base import BaseRegulation


class Regular(BaseRegulation):
    """
    Regulation defined as omega-regular expression (actually not omega for now).
    """
    def __init__(self, regulation):
        super(Regular, self).__init__(regulation)
        self.regulation = regex.compile(regulation)
        self.memory = 2

    def __str__(self):
        return "RE: " + str(self.regulation)

    def __repr__(self):
        # TODO
        return "type regular\n" + "\n".join(self.regulation)

    def filter(self, current_state, candidates):
        path = "".join(current_state.memory.history)
        return {rule: values for rule, values in candidates.items()
                if self.regulation.fullmatch(path + rule.label, partial=True) is not None}
    
    def check_labels(self, model_labels):
        patterns = self.regulation.pattern[1:-1].split("|")
        subpaterns_set = set()
        for pattern in patterns:
            subpaterns_set = subpaterns_set.union(set(pattern.split(";")))

        for subpattern in subpaterns_set:
            subregex = regex.compile(subpattern)
            if any(subregex.search(label) for label in model_labels):
                continue
            raise RegulationParsingError(
                f"Label in programmed regulation not present in model"
            )
        return True
