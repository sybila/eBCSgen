import unittest
import collections

from Core.Rate import Rate
from Core.Structure import StructureAgent
from Core.Atomic import AtomicAgent
from Core.Complex import Complex
from Core.Rule import Rule
from Core.Side import Side
from Core.Reaction import Reaction
from Parsing.ParseBCSL import Parser


class TestRule(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("S", "u")
        self.a2 = AtomicAgent("S", "p")
        self.a3 = AtomicAgent("B", "_")
        self.a4 = AtomicAgent("B", "-")
        self.a5 = AtomicAgent("B", "+")

        self.s1 = StructureAgent("K", {self.a1})
        self.s2 = StructureAgent("B", set())
        self.s3 = StructureAgent("K", {self.a2})
        self.s4 = StructureAgent("B", set())
        self.s5 = StructureAgent("D", {self.a3})
        self.s6 = StructureAgent("K", {self.a4})
        self.s7 = StructureAgent("K", {self.a5})

        self.c1 = Complex([self.s1, self.s2], "cyt")
        self.c2 = Complex([self.s3], "cyt")
        self.c3 = Complex([self.s2], "cyt")
        self.c4 = Complex([self.s5], "cell")

        #  rules

        sequence_1 = (self.s1, self.s2, self.s3, self.s4)
        mid_1 = 2
        compartments_1 = ["cyt"] * 4
        complexes_1 = [(0, 1), (2, 2), (3, 3)]
        pairs_1 = [(0, 2), (1, 3)]
        rate_1 = Rate("3.0*[K()::cyt]/2.0*v_1")

        self.r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

        sequence_2 = (self.s1, self.s2, self.s3, self.s4, self.s5)
        mid_2 = 2
        compartments_2 = ["cyt"] * 4 + ["cell"]
        complexes_2 = [(0, 1), (2, 2), (3, 3), (4, 4)]
        pairs_2 = [(0, 2), (1, 3), (None, 4)]
        rate_2 = Rate("3.0*[K()::cyt]/2.0*v_1")

        self.r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, rate_2)

        sequence_3 = (self.s6, self.s2, self.s5, self.s7, self.s4)
        mid_3 = 3
        compartments_3 = ["cyt"] * 2 + ["cell"] + ["cyt"] * 2
        complexes_3 = [(0, 1), (2, 2), (3, 3), (4, 4)]
        pairs_3 = [(0, 3), (1, 4), (2, None)]
        rate_3 = Rate("3.0*[K(T{3+})::cyt]/2.0*v_1")

        self.r3 = Rule(sequence_3, mid_3, compartments_3, complexes_3, pairs_3, rate_3)

        # special cases

        self.s1_s = StructureAgent("X", set())
        self.s2_s = StructureAgent("Y", set())
        self.s3_s = StructureAgent("Z", set())

        sequence_4 = (self.s1_s, )
        mid_4 = 1
        compartments_4 = ["rep"]
        complexes_4 = [(0, 0)]
        pairs_4 = [(0, None)]
        rate_4 = Rate("k1*[X()::rep]")

        self.r4 = Rule(sequence_4, mid_4, compartments_4, complexes_4, pairs_4, rate_4)

        sequence_5 = (self.s2_s, )
        mid_5 = 0
        compartments_5 = ["rep"]
        complexes_5 = [(0, 0)]
        pairs_5 = [(None, 0)]
        rate_5 = Rate("1.0/(1.0+([X()::rep])**4.0)")

        self.r5 = Rule(sequence_5, mid_5, compartments_5, complexes_5, pairs_5, rate_5)

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
        rate_c1 = Rate("3*[K()::cyt]/2*v_1")

        self.c1_c1 = Complex([self.s2_c1_u], "cyt")  # B(U{u})::cyt
        self.c1_c2 = Complex([self.s2_c1_p], "cyt")  # B(U{p})::cyt
        self.c1_c3 = Complex([self.s1_c1_a], "cyt")  # K(S{u},T{a})::cyt
        self.c1_c4 = Complex([self.s1_c1_i], "cyt")  # K(S{u},T{i})::cyt
        self.c1_c5 = Complex([self.s3_c1_a, self.s2_c1_u], "cyt")  # K(S{p},T{a}).B(U{u})::c
        self.c1_c6 = Complex([self.s3_c1_i, self.s2_c1_u], "cyt")  # K(S{p},T{i}).B(U{u})::c
        self.c1_c7 = Complex([self.s3_c1_i, self.s2_c1_p], "cyt")  # K(S{p},T{i}).B(U{p})::c
        self.c1_c8 = Complex([self.s3_c1_a, self.s2_c1_p], "cyt")  # K(S{p},T{a}).B(U{p})::c
        self.c1_c9 = Complex([self.s6_c1_p], "cyt")  # D(C{p})::cyt
        self.c1_c10 = Complex([self.s6_c1_u], "cyt")  # D(C{u})::cyt

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

        sequence_no_change = (self.s1_c1_a, self.s2_c1_u, self.s3_c1_a, self.s2_c1_u, self.s6_c1_p)
        self.rule_no_change = Rule(sequence_no_change, mid_c1, compartments_c1, complexes_c1, pairs_c1, rate_c1)

        # parsing

        self.parser = Parser("rule")

        self.rule_no_rate = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, None)

    def test_eq(self):
        self.assertEqual(self.r1, self.r1)

    def test_print(self):
        self.assertEqual(str(self.r1), "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt @ 3.0*[K()::cyt]/2.0*v_1")
        self.assertEqual(str(self.r2),
                         "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3.0*[K()::cyt]/2.0*v_1")

    def test_create_complexes(self):
        lhs = Side([self.c1])
        rhs = Side([self.c2, self.c3, self.c4])
        self.assertEqual(self.r2.create_complexes(), (lhs, rhs))

    def test_to_reaction(self):
        self.assertEqual(self.r2.to_reaction(), self.reaction1)

    def test_create_reactions(self):
        atomic_signature = {"T": {"a", "i"}, "U": {"p", "u"}, "C": {"p", "u"}, "S": {"p", "u"}}
        structure_signature = {"K": {"T", "S"}, "B": {"U"}, "D": {"C"}}
        self.assertEqual(self.rule_c1.create_reactions(atomic_signature, structure_signature),
                         self.reactions_c1)

        self.assertEqual(self.rule_no_change.create_reactions(atomic_signature, structure_signature),
                         {self.reaction_c1_1})

        rule_exp = "K(T{a}).K().K()::cyt => K(T{i}).K().K()::cyt @ k1*[K(T{a}).K().K()::cyt]"
        rule = self.parser.parse(rule_exp).data
        result = rule.create_reactions(atomic_signature, structure_signature)

        reactions = set()
        with open("Testing/reactions.txt") as file:
            for complex in file.readlines():
                rule = self.parser.parse(complex).data
                reactions.add(rule.to_reaction())

        self.assertEqual(result, reactions)

    def test_parser(self):
        rule_expr = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
        self.assertEqual(self.parser.parse(rule_expr).data, self.r2)

        rule_expr = "K(B{-}).B()::cyt + D(B{_})::cell => K(B{+})::cyt + B()::cyt @ 3*[K(T{3+})::cyt]/2*v_1"
        self.assertEqual(self.parser.parse(rule_expr).data, self.r3)

        rule_expr = "X()::rep => @ k1*[X()::rep]"
        self.assertEqual(self.parser.parse(rule_expr).data, self.r4)

        rule_expr = "=> Y()::rep @ 1/(1+([X()::rep])**4)"
        self.assertEqual(self.parser.parse(rule_expr).data, self.r5)

        rule_expr = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt"
        self.assertEqual(self.parser.parse(rule_expr).data, self.rule_no_rate)

    def test_compatible(self):
        self.assertTrue(self.r1.compatible(self.r2))
        self.assertFalse(self.r2.compatible(self.r1))

        rule_expr_1 = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
        rule_expr_2 = "K().B()::cyt => K()::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
        rule1 = self.parser.parse(rule_expr_1).data
        rule2 = self.parser.parse(rule_expr_2).data

        self.assertFalse(rule1.compatible(rule2))
        self.assertTrue(rule2.compatible(rule1))

    def test_reduce_context(self):
        rule_expr_1 = "K(S{u}).B{i}::cyt => K(S{p})::cyt + B{a}::cyt + D(B{_})::cell @ 3*[K(S{u}).B{i}::cyt]/2*v_1"
        rule1 = self.parser.parse(rule_expr_1).data

        rule_expr_2 = "K().B{_}::cyt => K()::cyt + B{_}::cyt + D()::cell @ 3*[K().B{_}::cyt]/2*v_1"
        rule2 = self.parser.parse(rule_expr_2).data

        self.assertEqual(rule1.reduce_context(), rule2)

    def test_exists_compatible_agent(self):
        complex_parser = Parser("rate_complex")
        agent = "K(S{a}).A{a}::cyt"
        complex = complex_parser.parse(agent).data.children[0]

        rule_expr = "K().A{i}::cyt => K().A{a}::cyt"
        rule = self.parser.parse(rule_expr).data

        self.assertTrue(rule.exists_compatible_agent(complex))
