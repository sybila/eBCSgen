import unittest
import collections
import numpy as np

from Core.Structure import StructureAgent
from Core.Atomic import AtomicAgent
from Core.Complex import Complex
from Core.Side import Side
from TS.State import State
import Parsing.ParseBCSL


class TestSide(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("S", "u")
        self.a2 = AtomicAgent("S", "p")
        self.a3 = AtomicAgent("T", "_")
        self.a4 = AtomicAgent("S", "_")
        self.a5 = AtomicAgent("T", "a")

        self.s1 = StructureAgent("K", {self.a1})
        self.s2 = StructureAgent("B", set())
        self.s3 = StructureAgent("K", {self.a2})
        self.s4 = StructureAgent("B", set())
        self.s5 = StructureAgent("D", {self.a3})
        self.s6 = StructureAgent("B", {self.a5, self.a2})

        self.c1 = Complex(collections.Counter({self.s2: 2}), "cyt")
        self.c2 = Complex(collections.Counter({self.s3: 1}), "cyt")
        self.c3 = Complex(collections.Counter({self.s2: 1}), "cyt")
        self.c4 = Complex(collections.Counter({self.s5: 1}), "cell")
        self.c5 = Complex(collections.Counter({self.s4: 1}), "cell")
        self.c6 = Complex(collections.Counter({self.s6: 1}), "cell")

        #  rules

        self.side1 = Side([self.c1, self.c2, self.c4])
        self.side2 = Side([self.c2, self.c3, self.c4])
        self.side3 = Side([self.c3, self.c4, self.c2])
        self.side4 = Side([self.c6, self.c1])
        self.side5 = Side([self.c5, self.c1])
        self.side6 = Side([self.c5, self.c1, self.c2])
        self.side7 = Side([self.c6, self.c1, self.c3, self.c4])

    def test_eq(self):
        self.assertEqual(self.side2, self.side3)
        self.assertNotEqual(self.side1, self.side2)

    def test_to_counter(self):
        self.assertEqual(self.side1.to_counter(), collections.Counter({self.c1: 1, self.c2: 1, self.c4: 1}))

    def test_to_vector(self):
        ordering = (self.c1, self.c2, self.c3, self.c4)
        self.assertEqual(self.side2.to_vector(ordering), State(np.array((0, 1, 1, 1))))

    def test_compatible(self):
        self.assertTrue(self.side5.compatible(self.side4))
        self.assertTrue(self.side5.compatible(self.side7))
        self.assertFalse(self.side6.compatible(self.side4))

    def test_exists_compatible_agent(self):
        self.assertTrue(self.side1.exists_compatible_agent(self.c1))
        self.assertFalse(self.side1.exists_compatible_agent(self.c3))

    def test_create_all_compatible(self):
        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")
        side_parser = Parsing.ParseBCSL.Parser("side")

        atomic_signature = {"A": {"+", "-"}, "B": {"HA", "HE"}, "S": {"a", "i"}, "T": {"u", "p"}}
        structure_signature = {"KaiB": {"A", "B"}, "KaiC": {"S", "T"}}

        results = set()
        with open("Testing/complexes_1.txt") as file:
            for complex in file.readlines():
                results.add(complex_parser.parse(complex).data.children[0])

        with open("Testing/complexes_2.txt") as file:
            for complex in file.readlines():
                results.add(complex_parser.parse(complex).data.children[0])

        side = "KaiC().KaiC().KaiC().KaiC().KaiC().KaiC()::cyt + 2 KaiB().KaiB().KaiB()::cyt"
        side = side_parser.parse(side).data.to_side()
        output_comples = side.create_all_compatible(atomic_signature, structure_signature)
        self.assertEqual(output_comples, results)
