import unittest
from Objects.Atomic import AtomicAgent


class TestState(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("T", "s")
        self.a2 = AtomicAgent("S", "a")
        self.a3 = AtomicAgent("T", "s")
        self.a4 = AtomicAgent("T", "_")
        self.a5 = AtomicAgent("T", "_")
        self.a6 = AtomicAgent("T", "p")
        self.a7 = AtomicAgent("T", "u")

    def test_eq(self):
        self.assertEqual(self.a1, self.a3)
        self.assertNotEqual(self.a1, self.a2)
        self.assertNotEqual(self.a1, self.a4)

    def test_print(self):
        self.assertEqual(str(self.a1), "T{s}")
        self.assertEqual(str(self.a4), "T{_}")

    def test_compatibility(self):
        self.assertTrue(self.a4.compatible(self.a1))
        self.assertFalse(self.a2.compatible(self.a1))
        self.assertFalse(self.a1.compatible(self.a4))

    def test_add_context(self):
        atomic_signature = {"T": {"u", "p"}}
        structure_signature = dict()
        self.assertEqual(self.a4.add_context(self.a5, atomic_signature, structure_signature),
                         {(self.a6, self.a6), (self.a7, self.a7)})
        self.assertEqual(self.a6.add_context(self.a6, atomic_signature, structure_signature),
                         {(self.a6, self.a6)})
        self.assertEqual(self.a4.add_context(-1, atomic_signature, structure_signature),
                         {(None, self.a6), (None, self.a7)})
