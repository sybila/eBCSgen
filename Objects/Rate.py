from TS.State import State


class Rate:
    def __init__(self, expression):
        self.expression = expression

    def __eq__(self, other):
        return self.expression == other.expression

    def __str__(self):
        return self.expression

    def vectorize(self, ordering: tuple):
        pass

    def evaluate(self, state: State) -> float:
        pass
