import unittest
import numpy as np
import pandas as pd

from Core.Rate import Rate
from Core.Structure import StructureAgent
from Core.Complex import Complex
from Parsing.ParseModel import Parser
from TS.State import State
from TS.VectorModel import VectorModel
from TS.VectorReaction import VectorReaction


class TestVectorModel(unittest.TestCase):
    def setUp(self):
        self.s1 = StructureAgent("X", set())
        self.s2 = StructureAgent("Y", set())
        self.s3 = StructureAgent("Z", set())

        self.c1 = Complex([self.s1], "rep")
        self.c2 = Complex([self.s2], "rep")
        self.c3 = Complex([self.s3], "rep")

        ordering = (self.c1, self.c2, self.c3)
        params = {"k1": 0.05, "k2": 0.1}

        self.rate_parser = Parser("rate")
        rate_expr = "1/(1+([X()::rep])**2)"
        rate_1 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_1.vectorize(ordering, params)

        rate_expr = "k1*[X()::rep]"
        rate_2 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_2.vectorize(ordering, params)

        rate_expr = "k2*[Z()::rep]"
        rate_3 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_3.vectorize(ordering, params)

        init = State(np.array([2.0, 1.0, 1.0]))

        vector_reactions = {VectorReaction(State(np.array([0.0, 0.0, 0.0])), State(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(State(np.array([1.0, 0.0, 0.0])), State(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(State(np.array([0.0, 0.0, 1.0])), State(np.array([1.0, 0.0, 0.0])), None)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)

        vector_reactions = {VectorReaction(State(np.array([0.0, 0.0, 0.0])), State(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(State(np.array([1.0, 0.0, 0.0])), State(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(State(np.array([0.0, 0.0, 1.0])), State(np.array([1.0, 0.0, 0.0])), rate_3)}

        self.vm_2 = VectorModel(vector_reactions, init, ordering, None)

        # test abstract model

        self.model_parser = Parser("model")

        self.model_abstract = \
            """#! rules
            => X()::rep @ k2*[T{_}::rep]
            T{a}::rep => T{i}::rep @ k1*[T{_}::rep]

            #! inits
            10 T{a}::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

    def test_compute_bound(self):
        self.assertEqual(self.vm_1.bound, 2)

    def test_deterministic_simulation(self):
        # simple rates
        data_simulated = self.vm_2.deterministic_simulation(3, 1/(6.022 * 10**23))
        data_loaded = pd.read_csv("Testing/simple_out.csv")

        pd.testing.assert_frame_equal(data_simulated, data_loaded)

        # more abstract rates

        model = self.model_parser.parse(self.model_abstract).data
        vector_model = model.to_vector_model()
        data_simulated = vector_model.deterministic_simulation(3, 1/(6.022 * 10**23))
        data_loaded = pd.read_csv("Testing/abstract_out.csv")

        pd.testing.assert_frame_equal(data_simulated, data_loaded)

        # to save datafram to csv file
        # data_simulated.to_csv("Testing/abstract_out.csv", index = None, header=True)

    def test_stochastic_simulation(self):
        model = self.model_parser.parse(self.model_abstract).data
        vector_model = model.to_vector_model()

        data_simulated = vector_model.stochastic_simulation(5, 4)
        # print("\n", data_simulated)
