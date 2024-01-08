import unittest

import Testing.objects_testing as objects


class TestStructure(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(objects.s15, objects.s19)
        self.assertNotEqual(objects.s15, objects.s16)
        self.assertNotEqual(objects.s15, objects.a2)  # comparing different classes

    def test_print(self):
        self.assertEqual(str(objects.s15), "strA(S{a},T{s})")
        self.assertEqual(str(objects.s18), "strD()")

    def test_compatibility(self):
        self.assertTrue(objects.s16.compatible(objects.s15))
        self.assertFalse(objects.s15.compatible(objects.s16))
        self.assertFalse(
            objects.s15.compatible(objects.a2)
        )  # comparing different classes

    def test_add_context(self):
        atomic_signature = {"T": {"s", "p"}, "S": {"i", "a"}}
        structure_signature = {"strA": {"T", "S"}}
        self.assertEqual(
            objects.s20.add_context(objects.s21, atomic_signature, structure_signature),
            {(objects.s15, objects.s23), (objects.s24, objects.s25)},
        )
        self.assertEqual(
            objects.s20.add_context(1, atomic_signature, structure_signature),
            {(objects.s15, None), (objects.s24, None)},
        )
        self.assertEqual(
            objects.s20.add_context(-1, atomic_signature, structure_signature),
            {(None, objects.s15), (None, objects.s24)},
        )

    def test_reduce_context(self):
        self.assertEqual(objects.s25.reduce_context(), objects.s26)

    def test_replace(self):
        self.assertEqual(objects.s21.replace(objects.s15), objects.s23)
        self.assertEqual(objects.s26.replace(objects.s15), objects.s15)
