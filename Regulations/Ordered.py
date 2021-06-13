from Regulations.Base import BaseRegulation


class Ordered(BaseRegulation):
    """
    Regulation defined as partial order on rules.
    Only rules not lower in the order are allowed to be used in the next step.
    """
    def __init__(self, regulation):
        super(Ordered, self).__init__(regulation)
        self.regulation = self.transitive_closure(self.regulation)
        self.memory = 1

    def transitive_closure(self, closure):
        """
        Computers transitive closure for partial order.

        TODO: needs to be optimised

        @param closure: given regulation
        @return: computed closure
        """
        while True:
            new_relations = set((x, w) for x, y in closure for q, w in closure if q == y)
            closure_until_now = closure | new_relations
            if closure_until_now == closure:
                return closure
            closure = closure_until_now

    def filter(self, current_state, candidates):
        if len(current_state.used_rules) == 0:
            return candidates
        last_rule = current_state.used_rules[-1]
        return {rule: values for rule, values in candidates.items() if not (last_rule, rule.label) in self.regulation}
