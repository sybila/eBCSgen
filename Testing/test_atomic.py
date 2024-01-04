import unittest
import Testing.objects_testing as objects


class TestAtomic(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(objects.a1, objects.a8)
        self.assertNotEqual(objects.a1, objects.a2)
        self.assertNotEqual(objects.a1, objects.a4)

    def test_print(self):
        self.assertEqual(str(objects.a1), "T{s}")
        self.assertEqual(str(objects.a4), "T{_}")

    def test_compatibility(self):
        self.assertTrue(objects.a4.compatible(objects.a1))
        self.assertFalse(objects.a2.compatible(objects.a1))
        self.assertFalse(objects.a1.compatible(objects.a4))

    def test_add_context(self):
        atomic_signature = {"T": {"u", "p"}}
        structure_signature = dict()
        self.assertEqual(
            objects.a4.add_context(objects.a4, atomic_signature, structure_signature),
            {(objects.a6, objects.a6), (objects.a7, objects.a7)},
        )
        self.assertEqual(
            objects.a6.add_context(objects.a6, atomic_signature, structure_signature),
            {(objects.a6, objects.a6)},
        )
        self.assertEqual(
            objects.a4.add_context(-1, atomic_signature, structure_signature),
            {(None, objects.a6), (None, objects.a7)},
        )

    def test_reduce_context(self):
        self.assertEqual(objects.a8.reduce_context(), objects.a4)

    def test_replace(self):
        self.assertEqual(objects.a4.replace(objects.a6), objects.a6)
        self.assertEqual(objects.a6.replace(objects.a7), objects.a6)
