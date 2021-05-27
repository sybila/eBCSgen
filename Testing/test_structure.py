import unittest
from Core.Structure import StructureAgent
from Core.Atomic import AtomicAgent


class TestStructure(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("T", "s")
        self.a2 = AtomicAgent("S", "a")
        self.a3 = AtomicAgent("T", "s")
        self.a4 = AtomicAgent("T", "_")
        self.a5 = AtomicAgent("T", "p")
        self.a6 = AtomicAgent("S", "i")

        self.s1 = StructureAgent("strA", {self.a1, self.a2})
        self.s2 = StructureAgent("strA", {self.a2, self.a4})
        self.s3 = StructureAgent("strA", {self.a4})
        self.s4 = StructureAgent("strD", set())
        self.s5 = StructureAgent("strA", {self.a2, self.a1})

        # context

        self.s6 = StructureAgent("strA", {self.a3})
        self.s7 = StructureAgent("strA", {self.a5})
        self.s8 = StructureAgent("strA", {self.a3, self.a2})
        self.s9 = StructureAgent("strA", {self.a5, self.a2})
        self.s10 = StructureAgent("strA", {self.a3, self.a6})
        self.s11 = StructureAgent("strA", {self.a5, self.a6})
        self.s12 = StructureAgent("strA", set())

    def test_eq(self):
        self.assertEqual(self.s1, self.s5)
        self.assertNotEqual(self.s1, self.s2)
        self.assertNotEqual(self.s1, self.a2)  # comparing different classes

    def test_print(self):
        self.assertEqual(str(self.s1), "strA(S{a},T{s})")
        self.assertEqual(str(self.s4), "strD()")

    def test_compatibility(self):
        self.assertTrue(self.s2.compatible(self.s1))
        self.assertFalse(self.s1.compatible(self.s2))
        self.assertTrue(self.s3.compatible(self.s1))
        self.assertFalse(self.s1.compatible(self.a2))  # comparing different classes

    def test_add_context(self):
        atomic_signature = {"T": {"s", "p"}, "S": {"i", "a"}}
        structure_signature = {"strA": {"T", "S"}}
        self.assertEqual(self.s6.add_context(self.s7, atomic_signature, structure_signature),
                         {(self.s8, self.s9), (self.s10, self.s11)})
        self.assertEqual(self.s6.add_context(1, atomic_signature, structure_signature),
                         {(self.s8, None), (self.s10, None)})
        self.assertEqual(self.s6.add_context(-1, atomic_signature, structure_signature),
                         {(None, self.s8), (None, self.s10)})

    def test_reduce_context(self):
        self.assertEqual(self.s11.reduce_context(), self.s12)

    def test_replace(self):
        self.assertEqual(self.s7.replace(self.s8), self.s9)
        self.assertEqual(self.s12.replace(self.s8), self.s8)
