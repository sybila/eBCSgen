import unittest
import numpy as np

from Core.Complex import Complex
from Core.Structure import StructureAgent
from TS.Edge import Edge
from TS.State import State, Vector, Memory
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

        self.s1 = State(Vector(np.array((1, 2, 3))), Memory(0))
        self.s2 = State(Vector(np.array((1, 2, 4))), Memory(0))
        self.s3 = State(Vector(np.array((1, 2, 5))), Memory(0))
        self.s4 = State(Vector(np.array((4, 2, 3))), Memory(0))
        self.hell = State(Vector(np.array((np.inf, np.inf, np.inf))), Memory(0), True)

        self.s1_reordered = State(Vector(np.array((3, 1, 2))), Memory(0))
        self.s2_reordered = State(Vector(np.array((4, 1, 2))), Memory(0))
        self.s3_reordered = State(Vector(np.array((5, 1, 2))), Memory(0))

        self.ts = TransitionSystem(tuple(), 5)
        self.ts.states_encoding = {1: self.s1, 2: self.s2}

        self.edge_1 = Edge(0, 1, 0.5)

        # equality of TS

        self.ts_eq_1 = TransitionSystem(ordering, 5)
        self.ts_eq_1.states_encoding = {0: self.s1, 1: self.s2, 2: self.s3}
        self.ts_eq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_eq_2 = TransitionSystem(ordering, 5)
        self.ts_eq_2.states_encoding = {1: self.s1, 2: self.s2, 0: self.s3}
        self.ts_eq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        self.ts_eq_3 = TransitionSystem(ordering_reordered, 5)
        self.ts_eq_3.states_encoding = {1: self.s1_reordered, 2: self.s2_reordered, 0: self.s3_reordered}
        self.ts_eq_3.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        # inequality of TS

        self.ts_neq_1 = TransitionSystem(ordering, 5)
        self.ts_neq_1.states_encoding = {0: self.s1, 1: self.s2, 2: self.s3}
        self.ts_neq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_neq_2 = TransitionSystem(ordering, 5)
        self.ts_neq_2.states_encoding = {1: self.s1, 2: self.s2, 0: self.s3}
        self.ts_neq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

        self.ts_neq_3 = TransitionSystem(ordering_wrong, 5)
        self.ts_neq_3.states_encoding = {1: self.s1, 2: self.s2, 0: self.s3}
        self.ts_neq_3.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

        # test bigger TS

        ordering = (self.c1, self.c2, self.c3, self.c4)

        self.ts_bigger = TransitionSystem(ordering, 5)
        self.ts_bigger.states_encoding = {1: self.s1, 2: self.s2, 0: self.s3, 3: self.s4}
        self.ts_bigger.edges = {Edge(1, 2, 0.8), Edge(0, 1, 0.5), Edge(1, 0, 0.3),
                                Edge(3, 1, 0.9), Edge(3, 2, 0.1), Edge(1, 3, 0.2)}

    def test_eq(self):
        self.assertEqual(self.ts_eq_1, self.ts_eq_2)
        self.assertEqual(self.ts_eq_1, self.ts_eq_3)
        self.assertNotEqual(self.ts_neq_1, self.ts_neq_2)
        self.assertNotEqual(self.ts_neq_1, self.ts_neq_3)

    def test_get_state_encoding(self):
        self.assertEqual(self.ts.states_encoding[2], self.s2)
        self.assertEqual(self.ts.states_encoding[1], self.s1)
        self.assertEqual(len(self.ts.states_encoding), 2)

    def test_add_edge(self):
        self.assertEqual(Edge(0, 1, 0.5), self.edge_1)

    def test_hash_edge(self):
        self.assertNotEqual(hash(Edge(1, 2, 0.3)), hash(Edge(2, 1, 0.3)))

    def test_edge_comparision(self):
        self.assertTrue(Edge(1, 2, 0.3) < Edge(2, 2, 0.3))
        self.assertTrue(Edge(1, 2, 0.3) < Edge(1, 3, 0.3))
        self.assertFalse(Edge(1, 2, 0.3) > Edge(2, 2, 0.3))
        self.assertTrue(Edge(4, 0, 0.3) < Edge(5, 2, 0.3))

    def test_sort_edges(self):
        edges = {Edge(1, 2, 0.3), Edge(2, 2, 0.3), Edge(4, 0, 0.3), Edge(4, 1, 0.3), Edge(5, 2, 0.3), Edge(1, 3, 0.3)}
        edges_sorted = [Edge(1, 2, 0.3), Edge(1, 3, 0.3), Edge(2, 2, 0.3),
                        Edge(4, 0, 0.3), Edge(4, 1, 0.3), Edge(5, 2, 0.3)]
        self.assertEqual(sorted(edges), edges_sorted)

    def test_change_hell(self):
        ordering = (self.c1, self.c2, self.c3, self.c4)
        ts = TransitionSystem(ordering, 4)
        ts.states_encoding = {1: self.s1, 2: self.s2, 0: self.s3, 3: self.hell}
        ts.change_hell()
        new_hell = State(Vector(np.array([5, 5, 5])), Memory(0), True)
        new_encoding = {1: self.s1, 2: self.s2, 0: self.s3, 3: new_hell}
        self.assertEqual(ts.states_encoding, new_encoding)
