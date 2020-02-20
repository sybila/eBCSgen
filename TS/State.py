import numpy as np


class State:
    def __init__(self, sequence: np.array):
        self.sequence = sequence

    def __eq__(self, other: 'State'):
        return (self.sequence == other.sequence).all()

    def __sub__(self, other: 'State'):
        return State(self.sequence - other.sequence)

    def __add__(self, other: 'State'):
        return State(self.sequence + other.sequence)

    def __mul__(self, other: 'State') -> np.array:
        return self.sequence * other.sequence

    def __str__(self):
        return str(self.sequence)

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.sequence)

    def __hash__(self):
        return hash(tuple(self.sequence))

    def check_negative(self, bound: float) -> bool:
        """
        Checks whether all values of State are are greater then 0 and smaller than given bound.

        :param bound: given bound
        :return: True if check was successful
        """
        return all(0 <= value <= bound for value in self.sequence)

    def filter_values(self, state: 'State') -> int:
        """
        Computed sum of individual values after intersection with given State.
        (used to indicate abstract agents in reaction-based setup).

        :param state: given State
        :return: resulting summation
        """
        return sum(self.sequence * state)

    def to_ODE_string(self) -> str:
        """
        Each non-zero value transforms to form y[i] where i is its particular position.
        Finally, groups these strings to a sum of them (in string manner).

        :return: string symbolic representation of state
        """
        return " + ".join(filter(None, ["y[" + str(i) + "]"
                                        if self.sequence[i] == 1 else None for i in range(len(self.sequence))]))
