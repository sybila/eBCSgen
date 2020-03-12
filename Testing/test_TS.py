import unittest
import numpy as np

from Core.Complex import Complex
from Core.Structure import StructureAgent
from TS.Edge import Edge
from TS.State import State
from TS.TransitionSystem import TransitionSystem


class TestTransitionSystem(unittest.TestCase):
    def setUp(self):
        self.str1 = StructureAgent("X", set())
        self.str2 = StructureAgent("Y", set())
        self.str3 = StructureAgent("Z", set())
        self.str4 = StructureAgent("W", set())

        self.c1 = Complex([self.str1], "rep")
        self.c2 = Complex([self.str2], "rep")
        self.c3 = Complex([self.str3], "rep")
        self.c4 = Complex([self.str4], "rep")

        ordering = (self.c1, self.c2, self.c3)
        ordering_wrong = (self.c1, self.c2, self.c3, self.c4),
        ordering_reordered = (self.c3, self.c1, self.c2)

        self.s1 = State(np.array((1, 2, 3)))
        self.s2 = State(np.array((1, 2, 4)))
        self.s3 = State(np.array((1, 2, 5)))

        self.s1_reordered = State(np.array((3, 1, 2)))
        self.s2_reordered = State(np.array((4, 1, 2)))
        self.s3_reordered = State(np.array((5, 1, 2)))

        self.ts = TransitionSystem(tuple())
        self.ts.states_encoding = {self.s1: 1, self.s2: 2}

        self.edge_1 = Edge(0, 1, 0.5)

        # equality of TS

        self.ts_eq_1 = TransitionSystem(ordering)
        self.ts_eq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2}
        self.ts_eq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_eq_2 = TransitionSystem(ordering)
        self.ts_eq_2.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_eq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        self.ts_eq_3 = TransitionSystem(ordering_reordered)
        self.ts_eq_3.states_encoding = {self.s1_reordered: 1, self.s2_reordered: 2, self.s3_reordered: 0}
        self.ts_eq_3.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        # inequality of TS

        self.ts_neq_1 = TransitionSystem(ordering)
        self.ts_neq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2}
        self.ts_neq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_neq_2 = TransitionSystem(ordering)
        self.ts_neq_2.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_neq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

        self.ts_neq_3 = TransitionSystem(ordering_wrong)
        self.ts_neq_3.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_neq_3.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

    def test_eq(self):
        self.assertEqual(self.ts_eq_1, self.ts_eq_2)
        self.assertEqual(self.ts_eq_1, self.ts_eq_3)
        self.assertNotEqual(self.ts_neq_1, self.ts_neq_2)
        self.assertNotEqual(self.ts_neq_1, self.ts_neq_3)

    def test_get_state_encoding(self):
        self.assertEqual(self.ts.states_encoding[self.s2], 2)
        self.assertEqual(self.ts.states_encoding[self.s1], 1)
        self.assertEqual(len(self.ts.states_encoding), 2)

    def test_add_edge(self):
        self.assertEqual(self.ts.new_edge(0, 1, 0.5), self.edge_1)

    def test_hash_edge(self):
        self.assertNotEqual(hash(Edge(1, 2, 0.3)), hash(Edge(2, 1, 0.3)))
