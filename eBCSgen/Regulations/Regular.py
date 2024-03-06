import regex
from itertools import permutations

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
        patterns = self.regulation.pattern[1:-1].split('|')
        # Generate all permutations of the label in the set
        all_permutations = [''.join(p) for i in range(len(model_labels)) for p in permutations(model_labels, i+1)]
        # Check if the regex matches any permutation
        for pattern in patterns:
            subregex = regex.compile(pattern)
            if any(subregex.search(p) for p in all_permutations):
                continue
            return False
        return True
