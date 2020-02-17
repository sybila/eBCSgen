import unittest
import collections
import numpy as np

from Core.Model import Model
from Core.Rate import Rate
from Core.Structure import StructureAgent
from Core.Complex import Complex
from Core.Rule import Rule
from Parsing.ParseModel import Parser
from TS.State import State
from TS.VectorModel import VectorModel
from TS.VectorReaction import VectorReaction


class TestModel(unittest.TestCase):
    def setUp(self):

        # agents

        self.s1 = StructureAgent("X", set())
        self.s2 = StructureAgent("Y", set())
        self.s3 = StructureAgent("Z", set())

        self.c1 = Complex([self.s1], "rep")
        self.c2 = Complex([self.s2], "rep")
        self.c3 = Complex([self.s3], "rep")

        #  rules

        sequence_1 = (self.s1, )
        mid_1 = 1
        compartments_1 = ["rep"]
        complexes_1 = [(0, 0)]
        pairs_1 = [(0, None)]
        rate_1 = Rate("k1*[X()::rep]")

        self.r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

        sequence_2 = (self.s3, self.s1)
        mid_2 = 1
        compartments_2 = ["rep"] * 2
        complexes_2 = [(0, 0), (1, 1)]
        pairs_2 = [(0, 1)]

        self.r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, None)

        sequence_3 = (self.s2, )
        mid_3 = 0
        compartments_3 = ["rep"]
        complexes_3 = [(0, 0)]
        pairs_3 = [(None, 0)]
        rate_3 = Rate("1/(1+([X()::rep])^4)")

        self.r3 = Rule(sequence_3, mid_3, compartments_3, complexes_3, pairs_3, rate_3)

        # inits

        self.inits = collections.Counter({self.c1: 2, self.c2: 1})

        # defs

        self.defs = {'k1': 0.05, 'k2': 0.12}

        self.model = Model({self.r1, self.r2, self.r3}, self.inits, self.defs, None)
        # model

        self.model_str_1 = """
        #! rules
        X()::rep => @ k1*[X()::rep]
        Z()::rep => X()::rep
        => Y()::rep @ 1/(1+([X()::rep])^4)

        #! inits
        2 X()::rep
        Y()::rep
        
        #! definitions
        k1 = 0.05
        k2 = 0.12
        """

        self.model_parser = Parser("model")

        self.model_str_2 = """
        #! rules
        X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
        X(T{a})::rep => X(T{o})::rep @ k2*[Z()::rep]
        => Y(P{f})::rep @ 1/(1+([X()::rep])^4)

        #! inits
        2 X(K{c}, T{e}).X(K{c}, T{j})::rep
        Y(P{g}, N{l})::rep

        #! definitions
        k1 = 0.05
        k2 = 0.12
        """

        # vectors

        ordering = (self.c1, self.c2, self.c3)

        self.rate_parser = Parser("rate")
        rate_expr = "1/(1+([X()::rep])^4)"
        rate_1 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_1.vectorize(ordering, dict())

        rate_expr = "k1*[X()::rep]"
        rate_2 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_2.vectorize(ordering, {"k1": 0.05})

        init = State(np.array([2.0, 1.0, 0.0]))

        vector_reactions = {VectorReaction(State(np.array([0.0, 0.0, 0.0])), State(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(State(np.array([1.0, 0.0, 0.0])), State(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(State(np.array([0.0, 0.0, 1.0])), State(np.array([1.0, 0.0, 0.0])), None)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)

        # wrong models

        self.model_wrong_1 = \
            """#! rules
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
            X(T{a})::rep => X(T{o}):rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(1+([X()::rep])^4)

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

        self.model_wrong_2 = \
            """#! rules
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
            X(T{a})::rep = X(T{o})::rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(1+([X()::rep])^4)

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

    def test_parser(self):
        self.assertEqual(self.model_parser.parse(self.model_str_1).data, self.model)

    def test_signatures(self):
        model = self.model_parser.parse(self.model_str_2).data
        self.assertEqual(model.atomic_signature, {'K': {'c', 'i', 'p'}, 'T': {'e', 'a', 'o', 'j'},
                                                  'P': {'g', 'f'}, 'N': {'l'}})
        self.assertEqual(model.structure_signature, {'X': {'K', 'T'}, 'Y': {'P', 'N'}})

    def test_to_vector_model(self):
        model = self.model_parser.parse(self.model_str_1).data
        self.assertTrue(model.to_vector_model() == self.vm_1)

    def test_parser_errors(self):
        self.model_parser.parse(self.model_wrong_1)
        self.assertEqual(self.model_parser.parse(self.model_wrong_1).data,
                         {"unexpected": ":", "expected": {'::', '.'}, "line": 3, "column": 36})

        self.assertEqual(self.model_parser.parse(self.model_wrong_2).data,
                         {"unexpected": "=", "expected": {'#! inits', ']', '#! definitions', '=>', '@', 'DIGIT', '+'},
                          "line": 3, "column": 26})

