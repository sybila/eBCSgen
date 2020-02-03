import numpy as np


class State:
    def __init__(self, sequence: np.array):
        self.sequence = sequence

    def __eq__(self, other):
        return (self.sequence == other.sequence).all()

    def __sub__(self, other):
        return State(self.sequence - other.sequence)

    def check_negative(self):
        return all(value > 0 for value in self.sequence)
