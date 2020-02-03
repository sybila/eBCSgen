import unittest
import collections

from Objects.Structure import StructureAgent
from Objects.Atomic import AtomicAgent
from Objects.Complex import Complex


class TestState(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("T", "s")
        self.a2 = AtomicAgent("S", "i")
        self.a3 = AtomicAgent("U", "a")
        self.a4 = AtomicAgent("T", "_")
        self.a5 = AtomicAgent("U", "_")
        self.a6 = AtomicAgent("S", "_")

        self.s1 = StructureAgent("X", {self.a1})
        self.s2 = StructureAgent("A", {self.a2, self.a3})
        self.s3 = StructureAgent("X", {self.a4})
        self.s4 = StructureAgent("A", {self.a2, self.a5})
        self.s5 = StructureAgent("A", {self.a6, self.a3})

        self.c1 = Complex(collections.Counter({self.s1: 1, self.s2: 2}), "cyt")
        self.c2 = Complex(collections.Counter({self.s3: 1, self.s4: 1, self.s5: 1}), "cyt")
        self.c3 = Complex(collections.Counter({self.s2: 2, self.s1: 1}), "cyt")
        self.c4 = Complex(collections.Counter({self.s2: 2, self.s1: 1}), "cell")

        self.large_c1 = Complex(collections.Counter({self.s4: 6, self.s3: 5}), "cell")
        self.large_c2 = Complex(collections.Counter({self.s5: 7, self.s3: 6}), "cell")

    def test_eq(self):
        self.assertEqual(self.c1, self.c3)
        self.assertNotEqual(self.c1, self.c4)

    def test_print(self):
        self.assertEqual(str(self.c1), "A(S{i},U{a}).A(S{i},U{a}).X(T{s})::cyt")
        self.assertEqual(str(self.c2), "A(S{_},U{a}).A(S{i},U{_}).X(T{_})::cyt")

    def test_compatibility(self):
        self.assertTrue(self.c2.compatible(self.c1))
        self.assertFalse(self.c1.compatible(self.c2))
        self.assertFalse(self.c2.compatible(self.c4))
        self.assertFalse(self.large_c1.compatible(self.large_c2))
