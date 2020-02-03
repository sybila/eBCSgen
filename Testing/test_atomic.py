import unittest
from Objects.Atomic import AtomicAgent


class TestState(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("T", "s")
        self.a2 = AtomicAgent("S", "a")
        self.a3 = AtomicAgent("T", "s")
        self.a4 = AtomicAgent("T", "_")

    def test_eq(self):
        self.assertEqual(self.a1, self.a3)
        self.assertNotEqual(self.a1, self.a2)
        self.assertNotEqual(self.a1, self.a4)

    def test_print(self):
        self.assertEqual(str(self.a1), "T{s}")
        self.assertEqual(str(self.a4), "T{_}")

    def test_compatibility(self):
        self.assertFalse(self.a4.compatible(self.a1))
        self.assertFalse(self.a2.compatible(self.a1))
        self.assertTrue(self.a1.compatible(self.a4))
