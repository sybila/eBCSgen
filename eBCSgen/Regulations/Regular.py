import regex

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
        positions = [False] * len(self.regulation.pattern)
        for label in model_labels:
            match = regex.search(label, self.regulation.pattern)
            while match is not None:
                for i in range(match.start(), match.end()):
                    positions[i] = True
                match = regex.search(label, self.regulation.pattern, pos=match.end())

        for i, position in enumerate(positions):
            if not position and self.regulation.pattern[i] not in ".*+?^${}()[]|\\":
                return False
        return True
