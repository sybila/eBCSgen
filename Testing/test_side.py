import unittest
import collections
import numpy as np

from Objects.Structure import StructureAgent
from Objects.Atomic import AtomicAgent
from Objects.Complex import Complex
from Objects.Side import Side
from TS.State import State


class TestState(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("S", "u")
        self.a2 = AtomicAgent("S", "p")
        self.a3 = AtomicAgent("T", "_")

        self.s1 = StructureAgent("K", {self.a1})
        self.s2 = StructureAgent("B", set())
        self.s3 = StructureAgent("K", {self.a2})
        self.s4 = StructureAgent("B", set())
        self.s5 = StructureAgent("D", {self.a3})

        self.c1 = Complex(collections.Counter({self.s2: 2}), "cyt")
        self.c2 = Complex(collections.Counter({self.s3: 1}), "cyt")
        self.c3 = Complex(collections.Counter({self.s2: 1}), "cyt")
        self.c4 = Complex(collections.Counter({self.s5: 1}), "cell")

        #  rules

        self.side1 = Side([self.c1, self.c2, self.c4])
        self.side2 = Side([self.c2, self.c3, self.c4])
        self.side3 = Side([self.c3, self.c4, self.c2])

    def test_eq(self):
        self.assertEqual(self.side2, self.side3)
        self.assertNotEqual(self.side1, self.side2)

    def test_to_counter(self):
        self.assertEqual(self.side1.to_counter(), collections.Counter({self.c1: 1, self.c2: 1, self.c4: 1}))

    def test_to_vector(self):
        ordering = (self.c1, self.c2, self.c3, self.c4)
        self.assertEqual(self.side2.to_vector(ordering), State(np.array((0, 1, 1, 1))))
