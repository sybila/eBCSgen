import unittest
import numpy as np

from TS.Edge import Edge
from TS.State import State
from TS.TransitionSystem import TransitionSystem


class TestTransitionSystem(unittest.TestCase):
    def setUp(self):
        self.s1 = State(np.array((1, 2, 3)))
        self.s2 = State(np.array((5, 4, 3)))
        self.s3 = State(np.array((2, 4, 6)))

        self.ts = TransitionSystem(tuple())
        self.ts.states_encoding = {self.s1: 0, self.s2: 1}

        self.edge_1 = Edge(0, 1, 0.5)

    def test_get_state_encoding(self):
        self.assertEqual(self.ts.get_state_encoding(self.s2), 1)
        self.assertEqual(self.ts.get_state_encoding(self.s3), 2)
        self.assertEqual(len(self.ts.states_encoding), 3)

    def test_add_edge(self):
        self.assertEqual(self.ts.add_edge(self.s1, self.s2, 0.5), self.edge_1)
