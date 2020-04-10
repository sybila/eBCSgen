import unittest

from Core.Structure import StructureAgent
from Core.Atomic import AtomicAgent
from Core.Complex import Complex


class TestComplex(unittest.TestCase):
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
        self.s6 = StructureAgent("A", set())

        self.c1 = Complex([self.s1, self.s2, self.s2], "cyt")
        self.c2 = Complex([self.s3, self.s4, self.s5], "cyt")
        self.c3 = Complex([self.s2, self.s2, self.s1], "cyt")
        self.c4 = Complex([self.s2, self.s2, self.s1], "cell")

        self.c5 = Complex([self.s2, self.s4, self.a1], "cell")
        self.c6 = Complex([self.s6, self.s6, self.a4], "cell")

        self.large_c1 = Complex([self.s4] * 6 + [self.s3] * 5, "cell")
        self.large_c2 = Complex([self.s5] * 7 + [self.s3] * 6, "cell")

    def test_eq(self):
        self.assertEqual(self.c1, self.c3)
        self.assertNotEqual(self.c1, self.c4)

    def test_print(self):
        self.assertEqual(str(self.c1), "X(T{s}).A(S{i},U{a}).A(S{i},U{a})::cyt")
        self.assertEqual(str(self.c2), "X(T{_}).A(S{i},U{_}).A(S{_},U{a})::cyt")

    def test_compatibility(self):
        self.assertTrue(self.c2.compatible(self.c1))
        self.assertFalse(self.c1.compatible(self.c2))
        self.assertFalse(self.c2.compatible(self.c4))
        self.assertFalse(self.large_c1.compatible(self.large_c2))

    def test_to_PRISM_code(self):
        self.assertEqual(self.c1.to_PRISM_code(5), "VAR_5")

    def test_reduce_context(self):
        self.assertEqual(self.c5.reduce_context(), self.c6)
