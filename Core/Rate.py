import numpy as np
import sympy
from lark import Transformer, Tree

from TS.State import State


class Rate:
    def __init__(self, expression):
        self.expression = expression

    def __eq__(self, other):
        return self.expression == other.expression

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.expression if type(self.expression) == str else "".join(to_string(self.expression))

    def vectorize(self, ordering: tuple, definitions: dict) -> list:
        """
        Converts all occurrences of Complexes (resp. sub trees named agent)
        with its vector representation. These are directly replaced within
        the tree expression.

        Moreover, in the process parameters are replaces with their values
        (if given).

        :param ordering: given tuple of Complexes
        :param definitions: dict of (param_name, value)
        :return: list of transformed States (just for testing)
        """
        vec = Vectorizer(ordering, definitions)
        self.expression = vec.transform(self.expression)
        return vec.visited

    def evaluate(self, state: State):
        """
        Evaluates all occurrences of States to a float using Evaluater.
        It is done as intersection of particular state with given state
        and sum of resulting elements.

        :param state: given state
        :return: Sympy object for expression representation
        """
        evaluater = Evaluater(state)
        result = evaluater.transform(self.expression)
        return sympy.sympify("".join(to_string(result)))

    def to_symbolic(self):
        """
        Translates rate from vector representation to symbolic one
        as a sum of particular components.
        e.g. [1, 0, 1] -> (x_0 + x_2)
        """
        transformer = SymbolicAgents()
        self.expression = transformer.transform(self.expression)

# Transformers for Tree


class SymbolicAgents(Transformer):
    def agent(self, vector):
        vector = "(" + vector[0].to_ODE_string() + ")"
        return Tree("agent", [vector])


class Vectorizer(Transformer):
    def __init__(self, ordering, definitions):
        super(Transformer, self).__init__()
        self.ordering = ordering
        self.definitions = definitions
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

    def rate_agent(self, matches):
        return matches[1]

    def param(self, matches):
        return self.definitions.get(str(matches[0]), str(matches[0]))


class Evaluater(Transformer):
    def __init__(self, state):
        super(Transformer, self).__init__()
        self.state = state

    def agent(self, state):
        return sum(self.state * state[0])


def to_string(tree):
    if type(tree) == Tree:
        return sum(list(map(to_string, tree.children)), [])
    else:
        return [str(tree)]
