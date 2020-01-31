import unittest
from TS.State import State


class TestState(unittest.TestCase):
    def setUp(self):
        self.s1 = State((1, 2, 3))
        self.s2 = State((5, 4, 3))
        self.s3 = State((5, 4, 3, 2))
        self.s4 = State((2, 2, 2, 1))

    def test_sub(self):
        self.assertEqual(self.s1 - self.s2, State((-4, -2, 0)))
        self.assertEqual(self.s3 - self.s4, State((3, 2, 1, 1)))
        with self.assertRaises(ValueError):
            self.s2 - self.s3

    def test_check_negative(self):
        self.assertFalse((self.s1 - self.s2).check_negative())
        self.assertTrue((self.s3 - self.s4).check_negative())
