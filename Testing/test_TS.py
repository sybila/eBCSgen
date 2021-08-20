import unittest
import numpy as np

from Core.Complex import Complex
from Core.Structure import StructureAgent
from TS.Edge import Edge
from TS.State import MemorylessState
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

        self.s1 = MemorylessState(np.array((1, 2, 3)))
        self.s2 = MemorylessState(np.array((1, 2, 4)))
        self.s3 = MemorylessState(np.array((1, 2, 5)))
        self.s4 = MemorylessState(np.array((4, 2, 3)))
        self.hell = MemorylessState(np.array((np.inf, np.inf, np.inf)))
        self.hell.is_inf = True

        self.s1_reordered = MemorylessState(np.array((3, 1, 2)))
        self.s2_reordered = MemorylessState(np.array((4, 1, 2)))
        self.s3_reordered = MemorylessState(np.array((5, 1, 2)))

        self.ts = TransitionSystem(tuple(), 5)
        self.ts.states_encoding = {self.s1: 1, self.s2: 2}

        self.edge_1 = Edge(0, 1, 0.5)

        # equality of TS

        self.ts_eq_1 = TransitionSystem(ordering, 5)
        self.ts_eq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2}
        self.ts_eq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_eq_2 = TransitionSystem(ordering, 5)
        self.ts_eq_2.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_eq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        self.ts_eq_3 = TransitionSystem(ordering_reordered, 5)
        self.ts_eq_3.states_encoding = {self.s1_reordered: 1, self.s2_reordered: 2, self.s3_reordered: 0}
        self.ts_eq_3.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        # inequality of TS

        self.ts_neq_1 = TransitionSystem(ordering, 5)
        self.ts_neq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2}
        self.ts_neq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_neq_2 = TransitionSystem(ordering, 5)
        self.ts_neq_2.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_neq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

        self.ts_neq_3 = TransitionSystem(ordering_wrong, 5)
        self.ts_neq_3.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_neq_3.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

        # test bigger TS

        ordering = (self.c1, self.c2, self.c3, self.c4)

        self.ts_bigger = TransitionSystem(ordering, 5)
        self.ts_bigger.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0, self.s4: 3}
        self.ts_bigger.edges = {Edge(1, 2, 0.8), Edge(0, 1, 0.5), Edge(1, 0, 0.3),
                                Edge(3, 1, 0.9), Edge(3, 2, 0.1), Edge(1, 3, 0.2)}

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

    def test_ts_iterator(self):
        sorted_and_separated = [[Edge(0, 1, 0.5)], [Edge(1, 0, 0.3), Edge(1, 2, 0.8), Edge(1, 3, 0.2)],
                                [Edge(3, 1, 0.9), Edge(3, 2, 0.1)]]
        self.assertEqual(list(iter(self.ts_bigger)), sorted_and_separated)

    def test_change_hell(self):
        ordering = (self.c1, self.c2, self.c3, self.c4)
        ts = TransitionSystem(ordering, 4)
        ts.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0, self.hell: 3}
        ts.change_hell()
        new_hell = MemorylessState(np.array([5, 5, 5]))
        new_encoding = {self.s1: 1, self.s2: 2, self.s3: 0, new_hell: 3}
        self.assertEqual(ts.states_encoding, new_encoding)
