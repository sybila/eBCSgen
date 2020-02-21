import unittest
from TS.State import State
import numpy as np


class TestState(unittest.TestCase):
    def setUp(self):
        self.s1 = State(np.array((1, 2, 3)))
        self.s2 = State(np.array((5, 4, 3)))
        self.s3 = State(np.array((5, 4, 3, 2)))
        self.s4 = State(np.array((2, 2, 2, 1)))

    def test_sub(self):
        self.assertEqual(self.s1 - self.s2, State(np.array((-4, -2, 0))))
        self.assertEqual(self.s3 - self.s4, State(np.array((3, 2, 1, 1))))
        with self.assertRaises(ValueError):
            self.s2 - self.s3

    def test_check_negative(self):
        bound = 5
        self.assertFalse((self.s1 - self.s2).check_negative(bound))
        self.assertTrue((self.s3 - self.s4).check_negative(bound))

    def test_reorder(self):
        order = np.array([2, 0, 1])
        self.assertEqual(self.s1.reorder(order), State(np.array((3, 1, 2))))
