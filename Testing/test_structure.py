import unittest
from Objects.Structure import StructureAgent
from Objects.Atomic import AtomicAgent


class TestState(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("T", "s")
        self.a2 = AtomicAgent("S", "a")
        self.a3 = AtomicAgent("T", "s")
        self.a4 = AtomicAgent("T", "_")

        self.s1 = StructureAgent("strA", {self.a1, self.a2})
        self.s2 = StructureAgent("strA", {self.a2, self.a4})
        self.s3 = StructureAgent("strA", {self.a4})
        self.s4 = StructureAgent("strD", set())
        self.s5 = StructureAgent("strA", {self.a2, self.a1})

    def test_eq(self):
        self.assertEqual(self.s1, self.s5)
        self.assertNotEqual(self.s1, self.s2)

    def test_print(self):
        self.assertEqual(str(self.s1), "strA(S{a},T{s})")
        self.assertEqual(str(self.s4), "strD()")

    def test_compatibility(self):
        self.assertTrue(self.s2.compatible(self.s1))
        self.assertFalse(self.s1.compatible(self.s2))
        self.assertTrue(self.s3.compatible(self.s1))
