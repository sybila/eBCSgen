import unittest
import numpy as np

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

    def test_compute_bound(self):
        self.assertEqual(self.vm_1.bound, 2)
