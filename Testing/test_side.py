import unittest
import collections
import numpy as np

from eBCSgen.TS.State import State, Memory, Vector

import Testing.objects_testing as objects


class TestSide(unittest.TestCase):

    def test_eq(self):
        self.assertEqual(objects.side7, objects.side8)
        self.assertNotEqual(objects.side6, objects.side7)

    def test_to_counter(self):
        self.assertEqual(objects.side6.to_counter(), collections.Counter({objects.counter_c1: 1, objects.counter_c2: 1, objects.counter_c4: 1}))

    def test_to_vector(self):
        ordering = (objects.counter_c1, objects.counter_c2, objects.counter_c3, objects.counter_c4)
        self.assertEqual(objects.side7.to_vector(ordering), State(Vector(np.array((0, 1, 1, 1))), Memory(0)))

    def test_compatible(self):
        self.assertTrue(objects.side10.compatible(objects.side9))
        self.assertTrue(objects.side10.compatible(objects.side12))
        self.assertFalse(objects.side11.compatible(objects.side9))

    def test_exists_compatible_agent(self):
        self.assertTrue(objects.side6.exists_compatible_agent(objects.counter_c1))
        self.assertFalse(objects.side6.exists_compatible_agent(objects.counter_c3))

    def test_create_all_compatible(self):
        atomic_signature = {"A": {"+", "-"}, "B": {"HA", "HE"}, "S": {"a", "i"}, "T": {"u", "p"}}
        structure_signature = {"KaiB": {"A", "B"}, "KaiC": {"S", "T"}}

        results = set()
        with open("Testing/complexes_1.txt") as file:
            for complex in file.readlines():
                results.add(objects.rate_complex_parser.parse(complex).data.children[0])

        with open("Testing/complexes_2.txt") as file:
            for complex in file.readlines():
                results.add(objects.rate_complex_parser.parse(complex).data.children[0])

        side = "KaiC().KaiC().KaiC().KaiC().KaiC().KaiC()::cyt + 2 KaiB().KaiB().KaiB()::cyt"
        side = objects.side_parser.parse(side).data.to_side()
        output_comples = side.create_all_compatible(atomic_signature, structure_signature)
        self.assertEqual(output_comples, results)
