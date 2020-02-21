import unittest
from TS.State import State
import numpy as np


class TestState(unittest.TestCase):
    def setUp(self):
        self.s1 = State(np.array((1, 2, 3)))
        self.s2 = State(np.array((5, 4, 3)))
        self.s3 = State(np.array((5, 4, 3, 2)))
        self.s4 = State(np.array((2, 2, 2, 1)))
        self.s5 = State(np.array((7, 6, 5, 3)))
        self.s6 = State(np.array((1, 0, 0, 1, 0)))
        self.s_inf = State(np.array((np.inf, np.inf, np.inf)))

    def test_sub(self):
        self.assertEqual(self.s1 - self.s2, State(np.array((-4, -2, 0))))
        self.assertEqual(self.s3 - self.s4, State(np.array((3, 2, 1, 1))))
        with self.assertRaises(ValueError):
            self.s2 - self.s3

    def test_check_negative(self):
        self.assertFalse((self.s1 - self.s2).check_negative())
        self.assertTrue((self.s3 - self.s4).check_negative())

    def test_add_with_bound(self):
        bound = 5
        self.assertEqual(self.s1.add_with_bound(self.s2, bound), self.s_inf)
        bound = 8
        self.assertEqual(self.s3.add_with_bound(self.s4, bound), self.s5)

    def test_to_ODE_string(self):
        self.assertEqual(self.s6.to_ODE_string(), "y[0] + y[3]")

    def test_reorder(self):
        order = np.array([2, 0, 1])
        self.assertEqual(self.s1.reorder(order), State(np.array((3, 1, 2))))
