import collections
from copy import copy

import numpy as np


class Memory:
    def __init__(self, level: int):
        self.level = level
        self.history = []

    def __eq__(self, other: 'Memory') -> bool:
        return self.level == other.level and self.history == other.history

    def __copy__(self):
        mem = Memory(self.level)
        mem.history = copy(self.history)
        return mem

    def __hash__(self):
        return hash(tuple(self.history))

    def update_memory(self, label):
        if self.level == 1:
            self.history = [label]
        elif self.level == 2:
            self.history.append(label)


class Vector:
    def __init__(self, value: np.array):
        self.value = value

    def __str__(self):
        return str(tuple(self.value))

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.value)

    def __hash__(self):
        return hash(tuple(self.value))

    def __eq__(self, other: 'Vector') -> bool:
        return (self.value == other.value).all()

    def __sub__(self, other: 'Vector'):
        return Vector(self.value - other.value)

    def __add__(self, other: 'Vector'):
        return Vector(self.value + other.value)

    def __mul__(self, other: 'Vector') -> np.array:
        return self.value * other.value

    def __ge__(self, other: 'Vector') -> bool:
        return all(self.value >= other.value)

    def validate_bound(self, bound):
        return all(value <= bound for value in self.value)

    def set_hell(self):
        self.value = np.array([np.inf] * len(self.value))

    def reorder(self, indices: np.array) -> 'Vector':
        return Vector(copy(self.value[indices]))

    def check_intersection(self, other: 'Vector'):
        for i in range(len(self.value)):
            if self.value[i] > 0 and other.value[i] > 0:
                return True
        return False

    def filter_values(self, state: 'Vector') -> int:
        """
        Computed sum of individual values after intersection with given Vector.
        (used to indicate abstract agents in reaction-based setup).

        :param state: given Vector
        :return: resulting summation
        """
        return sum(self * state)

    def to_multiset(self, ordering):
        multiset = collections.Counter(zip(ordering, self.value))
        return Multiset(multiset)


class Multiset:
    def __init__(self, value: collections.Counter):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

    def __eq__(self, other: 'Multiset') -> bool:
        return self.value == other.value

    def __sub__(self, other: 'Multiset'):
        return Multiset(self.value - other.value)

    def __add__(self, other: 'Multiset'):
        return Multiset(self.value + other.value)

    def __ge__(self, other: 'Multiset') -> bool:
        return all([self.value[agent] >= other.value.get(agent, 0) for agent in self.value])

    def __hash__(self):
        return hash(frozenset(self.value.items()))

    def validate_bound(self, bound):
        return all([self.value[agent] <= bound for agent in self.value])

    def set_hell(self):
        self.value = collections.Counter()

    def reorder(self, indices: np.array) -> 'Multiset':
        raise NotImplementedError('Method not supported for multiset.')

    def check_intersection(self, other: 'Multiset'):
        return self.value & other.value

    def to_vector(self, ordering, is_hell):
        if not is_hell:
            vector = np.zeros(len(ordering))
            for agent in self.value:
                vector[ordering.index(agent)] = int(self.value[agent])
        else:
            vector = np.full(len(ordering), np.inf)
        return Vector(vector)


class State:
    def __init__(self, content, memory: Memory, is_hell=False):
        self.content = content
        self.memory = memory
        self.is_hell = is_hell

    def __str__(self):
        return str(self.content) + str(self.memory.history)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.content()) + hash(self.memory)

    def __sub__(self, other: 'State'):
        return State(self.content - other.content, copy(self.memory))

    def __add__(self, other: 'State'):
        return State(self.content + other.content, copy(self.memory))

    def update_state(self, consumed, produced, label, bound) -> 'State':
        """
        Creates a new state by subtracting consumed object and adding produced objects.
        If given bound is exceeded, special state labeled as hell is returned.

        :param consumed: consumed objects
        :param produced: produced objects
        :param label: label of rule/reaction used
        :param bound: maximal allowed bound on individual values
        :return: resulting State
        """
        updated_content = self.content - consumed + produced
        if not updated_content.validate_bound(bound):
            updated_content.set_hell()
            return State(updated_content, Memory(0), is_hell=True)

        updated_memory = copy(self.memory)
        updated_memory.update_memory(label)
        return State(updated_content, updated_memory)

    def reorder(self, indices: np.array):
        """
        Changes order of individual values according to given indices.
        Works only for vector variant.

        :param indices: array of indices
        """
        return State(self.content.reorder(indices), copy(self.memory))

    def to_vector(self, ordering):
        """
        Convert content from Multiset to Vector based on given ordering

        :param ordering: given ordering of agents
        """
        self.content = self.content.to_vector(ordering, self.is_hell)

    def check_intersection(self, other: 'State'):
        """
        Check if the states have common intersection.

        :param other: given other State
        :return: True if intersection is nonempty
        """
        return self.content.check_intersection(other.content)

    def check_AP(self, ap, ordering: tuple) -> bool:
        """
        Checks whether the State satisfies given AtomicProposition.
        Works only for vector variant.

        :param ap: given AtomicProposition
        :param ordering: position of corresponding Complex
        :return: True if satisfied
        """
        if self.is_hell:
            return False
        if ap.complex in ordering:
            operand = str(self.content.value[ordering.index(ap.complex)])
        else:
            indices = ap.complex.identify_compatible(ordering)
            vector = Vector(np.array([1 if i in indices else 0 for i in range(len(ordering))]))
            operand = str(self.content.filter_values(vector))
        sign = "==" if ap.sign == " = " else ap.sign
        return eval(operand + sign + str(ap.number))

    def to_PRISM_string(self, apostrophe=False) -> str:
        """
        Creates string representation for PRISM file.
        Works only for vector variant.

        :param apostrophe: indicates whether variables should be with the apostrophe
        :return: PRISM string representation
        """
        aps = "'" if apostrophe else ""
        vars = list(map(lambda i: '(VAR_{}{}={})'.format(i, aps, int(self.content.value[i])),
                        range(len(self.content.value))))
        return " & ".join(vars)

    def to_ODE_string(self) -> str:
        """
        Each non-zero value transforms to form y[i] where i is its particular position.
        Finally, groups these strings to a sum of them (in string manner).
        Works only for vector variant.

        :return: string symbolic representation of state
        """
        return " + ".join(filter(None, ["y[" + str(i) + "]" if self.content.value[i] == 1
                                        else None for i in range(len(self.content.value))]))
