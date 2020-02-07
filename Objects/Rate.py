import numpy as np
from lark import Transformer, Tree

from TS.State import State


class Rate:
    def __init__(self, expression):
        self.expression = expression

    def __eq__(self, other):
        return self.expression == other.expression

    def __str__(self):
        return self.expression

    def vectorize(self, ordering: tuple):
        vec = Vectorizer(ordering)
        vec.transform(self.expression)
        return vec.visited

    def evaluate(self, state: State) -> float:
        pass


class Vectorizer(Transformer):
    def __init__(self, ordering):
        super(Transformer, self).__init__()
        self.ordering = ordering
        self.visited = []

    def agent(self, complex):
        complex = complex[0]
        result = np.zeros(len(self.ordering))
        for i in range(len(self.ordering)):
            if complex.compatible(self.ordering[i]):
                result[i] = 1

        result = State(result)
        self.visited.append(result)
        return Tree("agent", [result])
