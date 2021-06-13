import collections
from copy import deepcopy

import numpy as np

import Core.Formula


class MemorylessState:
    def __init__(self, sequence: np.array):
        self.sequence = sequence
        self.is_inf = self.is_hell()

    def __eq__(self, other: 'MemorylessState'):
        return (self.sequence == other.sequence).all()

    def __sub__(self, other: 'MemorylessState'):
        return MemorylessState(self.sequence - other.sequence)

    def __add__(self, other: 'MemorylessState'):
        return MemorylessState(self.sequence + other.sequence)

    def __mul__(self, other: 'MemorylessState') -> np.array:
        return self.sequence * other.sequence

    def __ge__(self, other: 'MemorylessState') -> bool:
        return all(self.sequence >= other.sequence)

    def __str__(self):
        return str(tuple(self.sequence))

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.sequence)

    def __hash__(self):
        return hash(tuple(self.sequence))

    def check_negative(self) -> bool:
        """
        Checks whether all values of MemorylessState are are greater then 0.

        :return: True if check was successful
        """
        return all(0 <= value for value in self.sequence)

    def add_with_bound(self, target: 'MemorylessState', bound: int) -> 'MemorylessState':
        """
        Creates a new state as a sum with the target. If resulting state is smaller than given bound,
        it is returned, otherwise special infinite state is returned instead.

        :param target: given state to be added
        :param bound: maximal allowed bound on individual values
        :return: resulting MemorylessState
        """
        new_state = self + target
        if all(value <= bound for value in new_state.sequence):
            return new_state
        else:
            return MemorylessState(np.array([np.inf] * len(new_state)))

    def filter_values(self, state: 'MemorylessState') -> int:
        """
        Computed sum of individual values after intersection with given MemorylessState.
        (used to indicate abstract agents in reaction-based setup).

        :param state: given MemorylessState
        :return: resulting summation
        """
        return sum(self * state)

    def to_ODE_string(self) -> str:
        """
        Each non-zero value transforms to form y[i] where i is its particular position.
        Finally, groups these strings to a sum of them (in string manner).

        :return: string symbolic representation of state
        """
        return " + ".join(filter(None, ["y[" + str(i) + "]"
                                        if self.sequence[i] == 1 else None for i in range(len(self.sequence))]))

    def reorder(self, indices: np.array) -> 'MemorylessState':
        """
        Changes order of individual values according to given new indices.

        :param indices: array of indices
        :return: new reordered MemorylessState
        """
        return MemorylessState(self.sequence[indices])

    def is_hell(self):
        """
        Checks whether state is special "hell" infinite state.
        :return: True if is special
        """
        return all([np.isinf(i) for i in self.sequence])

    def check_AP(self, ap, ordering: tuple) -> bool:
        """
        Checks whether the MemorylessState satisfies given AtomicProposition.

        TBA : could be abstract !!!

        :param ap: given AtomicProposition
        :param ordering: position of corresponding Complex
        :return: True if satisfied
        """
        if ap.complex in ordering:
            operand = str(self.sequence[ordering.index(ap.complex)])
        else:
            indices = ap.complex.identify_compatible(ordering)
            state = MemorylessState(np.array([1 if i in indices else 0 for i in range(len(ordering))]))
            operand = str(self.filter_values(state))
        sign = "==" if ap.sign == " = " else ap.sign
        return eval(operand + sign + str(ap.number))

    def to_PRISM_string(self, apostrophe=False) -> str:
        """
        Creates string representation for PRISM file.

        :param apostrophe: indicates whether variables should be with the apostrophe
        :return: PRISM string representation
        """
        aps = "'" if apostrophe else ""
        vars = list(map(lambda i: "(VAR_{}{}={})".format(i, aps, self.sequence[i]), range(len(self))))
        return " & ".join(vars)


class MultisetState:
    def __init__(self, multiset):
        self.multiset = multiset
        self.is_inf = self.is_hell()

    def __str__(self):
        return str(self.multiset)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.multiset == other.multiset

    def __ge__(self, other) -> bool:
        return all([self.multiset[agent] >= other.multiset.get(agent, 0) for agent in self.multiset])

    def __hash__(self):
        return hash(frozenset(self.multiset.items()))

    def is_hell(self):
        """
        Checks whether state is special "hell" infinite state.
        :return: True if is special
        """
        return all([np.isinf(self.multiset[agent]) for agent in self.multiset])

    def update_state(self, consumed, produced, used_rule_label):
        consumed = collections.Counter(consumed)
        produced = collections.Counter(produced)
        new_state = MultisetState(deepcopy(self.multiset - consumed + produced))
        return new_state

    def to_vector(self, ordering):
        vector = np.zeros(len(ordering))
        for agent in self.multiset:
            vector[ordering.index(agent)] = self.multiset[agent]
        return MemorylessState(vector)


class OneStepMemoryState(MultisetState):
    def __init__(self, multiset):
        super().__init__(multiset)
        self.used_rules = []

    def __eq__(self, other):
        return self.multiset == other.multiset and self.used_rules == other.last_rule

    def __ge__(self, other) -> bool:
        return all([self.multiset[agent] >= other.multiset.get(agent, 0) for agent in self.multiset])

    def __hash__(self):
        return hash(frozenset(self.multiset.items())) + hash(self.used_rules[0])

    def update_state(self, consumed, produced, used_rule_label):
        consumed = collections.Counter(consumed)
        produced = collections.Counter(produced)
        new_state = OneStepMemoryState(deepcopy(self.multiset - consumed + produced))
        new_state.used_rules = [used_rule_label]
        return new_state


class FullMemoryState(MultisetState):
    def __init__(self, multiset):
        super().__init__(multiset)
        self.used_rules = []

    def __eq__(self, other):
        return self.multiset == other.multiset and self.used_rules == other.used_rules

    def __ge__(self, other) -> bool:
        return all([self.multiset[agent] >= other.multiset.get(agent, 0) for agent in self.multiset])

    def __hash__(self):
        return hash(frozenset(self.multiset.items())) + hash(tuple(self.used_rules))    

    def update_state(self, consumed, produced, used_rule_label):
        consumed = collections.Counter(consumed)
        produced = collections.Counter(produced)
        new_state = FullMemoryState(deepcopy(self.multiset - consumed + produced))
        new_state.used_rules.append(used_rule_label)
        return new_state

