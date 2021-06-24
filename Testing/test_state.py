import unittest
import numpy as np

import Parsing.ParseBCSL
from Core.Formula import AtomicProposition
from TS.State import MemorylessState


class TestState(unittest.TestCase):
    def setUp(self):
        self.s1 = MemorylessState(np.array((1, 2, 3)))
        self.s2 = MemorylessState(np.array((5, 4, 3)))
        self.s3 = MemorylessState(np.array((5, 4, 3, 2)))
        self.s4 = MemorylessState(np.array((2, 2, 2, 1)))
        self.s5 = MemorylessState(np.array((7, 6, 5, 3)))
        self.s6 = MemorylessState(np.array((1, 0, 0, 1, 0)))
        self.s_inf = MemorylessState(np.array((np.inf, np.inf, np.inf)))

        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")

        self.complex_1 = complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        self.complex_2 = complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        self.complex_3 = complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]

    def test_sub(self):
        self.assertEqual(self.s1 - self.s2, MemorylessState(np.array((-4, -2, 0))))
        self.assertEqual(self.s3 - self.s4, MemorylessState(np.array((3, 2, 1, 1))))
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
        self.assertEqual(self.s1.reorder(order), MemorylessState(np.array((3, 1, 2))))

    def test_check_AP(self):
        ordering = (self.complex_1, self.complex_2, self.complex_3)
        ap = AtomicProposition(self.complex_2, "<=", 2)
        self.assertTrue(self.s1.check_AP(ap, ordering))
        ap = AtomicProposition(self.complex_2, ">", 2)
        self.assertFalse(self.s1.check_AP(ap, ordering))

    def test_to_PRISM_string(self):
        self.assertEqual(self.s1.to_PRISM_string(), "(VAR_0=1) & (VAR_1=2) & (VAR_2=3)")
        self.assertEqual(self.s1.to_PRISM_string(True), "(VAR_0'=1) & (VAR_1'=2) & (VAR_2'=3)")