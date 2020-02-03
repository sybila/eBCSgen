import unittest
import collections

from Objects.Structure import StructureAgent
from Objects.Atomic import AtomicAgent
from Objects.Complex import Complex
from Objects.Rule import Rule
from Objects.Side import Side


class TestState(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("S", "u")
        self.a2 = AtomicAgent("S", "p")
        self.a3 = AtomicAgent("B", "_")

        self.s1 = StructureAgent("K", {self.a1})
        self.s2 = StructureAgent("B", set())
        self.s3 = StructureAgent("K", {self.a2})
        self.s4 = StructureAgent("B", set())
        self.s5 = StructureAgent("D", {self.a3})

        self.c1 = Complex(collections.Counter({self.s1: 1, self.s2: 1}), "cyt")
        self.c2 = Complex(collections.Counter({self.s3: 1}), "cyt")
        self.c3 = Complex(collections.Counter({self.s2: 1}), "cyt")
        self.c4 = Complex(collections.Counter({self.s5: 1}), "cell")

        #  rules

        sequence_1 = (self.s1, self.s2, self.s3, self.s4)
        mid_1 = 2
        compartments_1 = ["cyt"] * 4
        complexes_1 = [(0, 1), (2, 2), (3, 3)]
        pairs_1 = [(0, 2), (1, 3)]
        rate_1 = "3*[K()::cyt]/2*v_1"

        self.r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

        sequence_2 = (self.s1, self.s2, self.s3, self.s4, self.s5)
        mid_2 = 2
        compartments_2 = ["cyt"] * 4 + ["cell"]
        complexes_2 = [(0, 1), (2, 2), (3, 3), (4, 4)]
        pairs_2 = [(0, 2), (1, 3), (None, 4)]
        rate_2 = "3*[K()::cyt]/2*v_1"

        self.r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, rate_2)

    def test_eq(self):
        self.assertEqual(self.r1, self.r1)

    def test_print(self):
        self.assertEqual(str(self.r1), "B().K(S{u})::cyt => K(S{p})::cyt + B()::cyt @ 3*[K()::cyt]/2*v_1")
        self.assertEqual(str(self.r2),
                         "B().K(S{u})::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1")

    def test_create_complexes(self):
        lhs = Side([self.c1])
        rhs = Side([self.c2, self.c3, self.c4])
        self.assertEqual(self.r2.create_complexes(), (lhs, rhs))
