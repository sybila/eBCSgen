import numpy as np


class State:
    def __init__(self, sequence: np.array):
        self.sequence = sequence

    def __eq__(self, other):
        return (self.sequence == other.sequence).all()

    def __sub__(self, other):
        return State(self.sequence - other.sequence)

    def __mul__(self, other) -> np.array:
        return self.sequence * other.sequence

    def __str__(self):
        return str(self.sequence)

    def __repr__(self):
        return str(self)

    def check_negative(self, bound: int) -> bool:
        return all(0 <= value <= bound for value in self.sequence)

    def filter_values(self, state: 'State') -> int:
        return sum(self.sequence * state)
