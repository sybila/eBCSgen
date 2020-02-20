import unittest
import numpy as np

from TS.Edge import Edge
from TS.State import State
from TS.TransitionSystem import TransitionSystem


class TestTransitionSystem(unittest.TestCase):
    def setUp(self):
        self.s1 = State(np.array((1, 2, 3)))
        self.s2 = State(np.array((1, 2, 4)))
        self.s3 = State(np.array((1, 2, 5)))

        self.ts = TransitionSystem(tuple())
        self.ts.states_encoding = {self.s1: 0, self.s2: 1}

        self.edge_1 = Edge(0, 1, 0.5)

        # equality of TS

        self.ts_eq_1 = TransitionSystem(tuple())
        self.ts_eq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2}
        self.ts_eq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_eq_2 = TransitionSystem(tuple())
        self.ts_eq_2.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_eq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(2, 0, 1)}

        # inequality of TS

        self.ts_neq_1 = TransitionSystem(tuple())
        self.ts_neq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2}
        self.ts_neq_1.edges = {Edge(0, 1, 0.3), Edge(0, 2, 0.7), Edge(1, 2, 1)}

        self.ts_neq_2 = TransitionSystem(tuple())
        self.ts_neq_2.states_encoding = {self.s1: 1, self.s2: 2, self.s3: 0}
        self.ts_neq_2.edges = {Edge(1, 2, 0.3), Edge(1, 0, 0.7), Edge(0, 2, 1)}

    def test_eq(self):
        self.assertEqual(self.ts_eq_1, self.ts_eq_2)
        self.assertNotEqual(self.ts_neq_1, self.ts_neq_2)

    def test_get_state_encoding(self):
        self.assertEqual(self.ts.get_state_encoding(self.s2), 1)
        self.assertEqual(self.ts.get_state_encoding(self.s3), 2)
        self.assertEqual(len(self.ts.states_encoding), 3)

    def test_add_edge(self):
        self.assertEqual(self.ts.add_edge(self.s1, self.s2, 0.5), self.edge_1)
