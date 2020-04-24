import numpy as np
import sympy
from lark import Transformer, Tree

import TS.State


class Rate:
    def __init__(self, expression):
        self.expression = expression

    def __eq__(self, other):
        return self.expression == other.expression

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.expression if type(self.expression) == str else "".join(tree_to_string(self.expression))

    def __hash__(self):
        return hash(str(self))

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

    def evaluate(self, state) -> float:
        """
        Evaluates all occurrences of States to a float using Evaluater.
        It is done as intersection of particular state with given state
        and sum of resulting elements.

        If the result is nan, None is returned instead.

        :param state: given state
        :return: Sympy object for expression representation
        """
        evaluater = Evaluater(state)
        result = evaluater.transform(self.expression)

        try:
            value = sympy.sympify("".join(tree_to_string(result)), locals=evaluater.locals)
            if value == sympy.nan:
                return None
            return value
        except TypeError:
            return None

    def to_symbolic(self):
        """
        Translates rate from vector representation to symbolic one
        as a sum of particular components.
        e.g. [1, 0, 1] -> (x_0 + x_2)
        """
        transformer = SymbolicAgents()
        self.expression = transformer.transform(self.expression)

    def reduce_context(self) -> 'Rate':
        """
        Reduces context of all Complexes to minimum.

        :return: new Rate with reduced context
        """
        transformer = ContextReducer()
        expression = transformer.transform(self.expression)
        return Rate(expression)

# Transformers for Tree

class ContextReducer(Transformer):
    def agent(self, matches):
        return Tree("agent", [matches[0].reduce_context()])


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

        result = TS.State.State(result)
        self.visited.append(result)
        return Tree("agent", [result])

    def rate_agent(self, matches):
        return matches[1]

    def param(self, matches):
        return self.definitions.get(str(matches[0]), Tree("param", matches))


class Evaluater(Transformer):
    def __init__(self, state):
        super(Transformer, self).__init__()
        self.state = state
        self.locals = dict()

    def agent(self, state):
        return sum(self.state * state[0])

    def param(self, matches):
        name = matches[0]
        self.locals[name] = sympy.Symbol(name)
        return name


def tree_to_string(tree):
    if type(tree) == Tree:
        return sum(list(map(tree_to_string, tree.children)), [])
    else:
        return [str(tree)]
