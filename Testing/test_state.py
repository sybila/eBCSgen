import unittest
import numpy as np

import Parsing.ParseBCSL
from Core.Formula import AtomicProposition
from TS.State import State, Memory, Vector


class TestState(unittest.TestCase):
    def setUp(self):
        self.s1 = State(Vector(np.array((1, 2, 3))), Memory(0))
        self.s2 = State(Vector(np.array((5, 4, 3))), Memory(0))
        self.s3 = State(Vector(np.array((5, 4, 3, 2))), Memory(0))
        self.s4 = State(Vector(np.array((2, 2, 2, 1))), Memory(0))
        self.s5 = State(Vector(np.array((7, 6, 5, 3))), Memory(0))
        self.s6 = State(Vector(np.array((1, 0, 0, 1, 0))), Memory(0))
        self.s_inf = State(Vector(np.array((np.inf, np.inf, np.inf))), Memory(0), True)

        self.consumed_1 = Vector(np.array((0, 0, 0)))
        self.consumed_2 = Vector(np.array((0, 0, 0, 0)))
        self.produced_1 = Vector(np.array((5, 4, 3)))
        self.produced_2 = Vector(np.array((2, 2, 2, 1)))

        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")

        self.complex_1 = complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        self.complex_2 = complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        self.complex_3 = complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]

    def test_memory(self):
        # no memory
        mem = Memory(0)
        mem.update_memory('test')
        mem_expected = Memory(0)
        self.assertEqual(mem, mem_expected)

        # one step memory

        mem = Memory(1)
        mem.update_memory('test')
        mem_expected = Memory(1)
        mem_expected.history = ['test']
        self.assertEqual(mem, mem_expected)

        mem.update_memory('next')
        mem_expected = Memory(1)
        mem_expected.history = ['next']
        self.assertEqual(mem, mem_expected)

        # infinite memory

        mem = Memory(2)
        mem.update_memory('test')
        mem.update_memory('next')
        mem_expected = Memory(2)
        mem_expected.history = ['test', 'next']
        self.assertEqual(mem, mem_expected)

    def test_sub(self):
        self.assertEqual(self.s1 - self.s2, State(Vector(np.array((-4, -2, 0))), Memory(0)))
        self.assertEqual(self.s3 - self.s4, State(Vector(np.array((3, 2, 1, 1))), Memory(0)))
        with self.assertRaises(ValueError):
            self.s2 - self.s3

    def test_add_with_bound(self):
        bound = 5
        self.assertEqual(self.s1.update_state(self.consumed_1, self.produced_1, 'label', bound), self.s_inf)
        bound = 8
        self.assertEqual(self.s3.update_state(self.consumed_2, self.produced_2, 'label', bound), self.s5)

    def test_to_ODE_string(self):
        self.assertEqual(self.s6.to_ODE_string(), "y[0] + y[3]")

    def test_reorder(self):
        order = np.array([2, 0, 1])
        self.assertEqual(self.s1.reorder(order), State(Vector(np.array((3, 1, 2))), Memory(0)))

    def test_check_AP(self):
        ordering = (self.complex_1, self.complex_2, self.complex_3)
        ap = AtomicProposition(self.complex_2, "<=", 2)
        self.assertTrue(self.s1.check_AP(ap, ordering))
        ap = AtomicProposition(self.complex_2, ">", 2)
        self.assertFalse(self.s1.check_AP(ap, ordering))

    def test_to_PRISM_string(self):
        self.assertEqual(self.s1.to_PRISM_string(), "(VAR_0=1) & (VAR_1=2) & (VAR_2=3)")
        self.assertEqual(self.s1.to_PRISM_string(True), "(VAR_0'=1) & (VAR_1'=2) & (VAR_2'=3)")
