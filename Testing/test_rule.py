import unittest
import collections

from Objects.Structure import StructureAgent
from Objects.Atomic import AtomicAgent
from Objects.Complex import Complex
from Objects.Rule import Rule
from Objects.Side import Side
from Objects.Reaction import Reaction


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

        #  reactions

        lhs = Side([self.c1])
        rhs = Side([self.c2, self.c3, self.c4])

        self.reaction1 = Reaction(lhs, rhs, rate_2)

        #  create

        self.t_i = AtomicAgent("T", "i")
        self.t_a = AtomicAgent("T", "a")

        self.a4_p = AtomicAgent("C", "p")
        self.a4_u = AtomicAgent("C", "u")

        self.u2_c1_p = AtomicAgent("U", "p")
        self.u2_c1_u = AtomicAgent("U", "u")

        self.s6 = StructureAgent("D", set())
        self.s6_c1_p = StructureAgent("D", {self.a4_p})
        self.s6_c1_u = StructureAgent("D", {self.a4_u})

        self.s2_c1_p = StructureAgent("B", {self.u2_c1_p})
        self.s2_c1_u = StructureAgent("B", {self.u2_c1_u})

        self.s1_c1_a = StructureAgent("K", {self.a1, self.t_a})
        self.s1_c1_i = StructureAgent("K", {self.a1, self.t_i})

        self.s3_c1_a = StructureAgent("K", {self.a2, self.t_a})
        self.s3_c1_i = StructureAgent("K", {self.a2, self.t_i})

        sequence_c1 = (self.s1, self.s2, self.s3, self.s4, self.s6)
        mid_c1 = 2
        compartments_c1 = ["cyt"] * 5
        complexes_c1 = [(0, 0), (1, 1), (2, 3), (4, 4)]
        pairs_c1 = [(0, 2), (1, 3), (None, 4)]
        rate_c1 = "3*[K()::cyt]/2*v_1"

        self.c1_c1 = Complex(collections.Counter({self.s2_c1_u: 1}), "cyt")  # B(U{u})::cyt
        self.c1_c2 = Complex(collections.Counter({self.s2_c1_p: 1}), "cyt")  # B(U{p})::cyt
        self.c1_c3 = Complex(collections.Counter({self.s1_c1_a: 1}), "cyt")  # K(S{u},T{a})::cyt
        self.c1_c4 = Complex(collections.Counter({self.s1_c1_i: 1}), "cyt")  # K(S{u},T{i})::cyt
        self.c1_c5 = Complex(collections.Counter({self.s2_c1_u: 1, self.s3_c1_a: 1}), "cyt")  # B(U{u}).K(S{p},T{a})::c
        self.c1_c6 = Complex(collections.Counter({self.s2_c1_u: 1, self.s3_c1_i: 1}), "cyt")  # B(U{u}).K(S{p},T{i})::c
        self.c1_c7 = Complex(collections.Counter({self.s2_c1_p: 1, self.s3_c1_i: 1}), "cyt")  # B(U{p}).K(S{p},T{i})::c
        self.c1_c8 = Complex(collections.Counter({self.s2_c1_p: 1, self.s3_c1_a: 1}), "cyt")  # B(U{p}).K(S{p},T{a})::c
        self.c1_c9 = Complex(collections.Counter({self.s6_c1_p: 1}), "cyt")  # D(C{p})::cyt
        self.c1_c10 = Complex(collections.Counter({self.s6_c1_u: 1}), "cyt")  # D(C{u})::cyt

        self.rule_c1 = Rule(sequence_c1, mid_c1, compartments_c1, complexes_c1, pairs_c1, rate_c1)

        self.reaction_c1_1 = Reaction(Side([self.c1_c1, self.c1_c3]),
                                      Side([self.c1_c5, self.c1_c9]), rate_c1)
        self.reaction_c1_2 = Reaction(Side([self.c1_c1, self.c1_c3]),
                                      Side([self.c1_c5, self.c1_c10]), rate_c1)
        self.reaction_c1_3 = Reaction(Side([self.c1_c2, self.c1_c4]),
                                      Side([self.c1_c7, self.c1_c10]), rate_c1)
        self.reaction_c1_4 = Reaction(Side([self.c1_c1, self.c1_c4]),
                                      Side([self.c1_c6, self.c1_c9]), rate_c1)
        self.reaction_c1_5 = Reaction(Side([self.c1_c2, self.c1_c3]),
                                      Side([self.c1_c8, self.c1_c9]), rate_c1)
        self.reaction_c1_6 = Reaction(Side([self.c1_c2, self.c1_c3]),
                                      Side([self.c1_c8, self.c1_c10]), rate_c1)
        self.reaction_c1_7 = Reaction(Side([self.c1_c1, self.c1_c4]),
                                      Side([self.c1_c6, self.c1_c10]), rate_c1)
        self.reaction_c1_8 = Reaction(Side([self.c1_c2, self.c1_c4]),
                                      Side([self.c1_c7, self.c1_c9]), rate_c1)

        self.reactions_c1 = {self.reaction_c1_1, self.reaction_c1_2, self.reaction_c1_3, self.reaction_c1_4,
                             self.reaction_c1_5, self.reaction_c1_6, self.reaction_c1_7, self.reaction_c1_8}

        # context no change

        sequence_no_change = (self.s2_c1_u, self.s1_c1_a, self.s2_c1_u, self.s3_c1_a, self.s6_c1_p)
        self.rule_no_change = Rule(sequence_no_change, mid_c1, compartments_c1, complexes_c1, pairs_c1, rate_c1)

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

    def test_to_reaction(self):
        self.assertEqual(self.r2.to_reaction(), self.reaction1)

    def test_create_reactions(self):
        atomic_signature = {"T": {"a", "i"}, "U": {"p", "u"}, "C": {"p", "u"}}
        structure_signature = {"K": {"T", "S"}, "B": {"U"}, "D": {"C"}}
        self.assertEqual(self.rule_c1.create_reactions(atomic_signature, structure_signature),
                         self.reactions_c1)

        self.assertEqual(self.rule_no_change.create_reactions(atomic_signature, structure_signature),
                         {self.reaction_c1_1})
