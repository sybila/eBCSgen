import unittest

from eBCSgen.Core.Rule import Rule

import Testing.objects_testing as objects


class TestRule(unittest.TestCase):
    
    def test_eq(self):
        self.assertEqual(objects.r4, objects.r4)

    def test_print(self):
        self.assertEqual(str(objects.r4), "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt @ 3.0*[K()::cyt]/2.0*v_1")
        self.assertEqual(str(objects.r5),
                         "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3.0*[K()::cyt]/2.0*v_1")

    def test_create_complexes(self):
        self.assertEqual(objects.r5.create_complexes(), (objects.lhs, objects.rhs))

    def test_to_reaction(self):
        self.assertEqual(objects.r5.to_reaction(), objects.reaction1)

    def test_create_reactions(self):
        atomic_signature = {"T": {"a", "i"}, "U": {"p", "u"}, "C": {"p", "u"}, "S": {"p", "u"}}
        structure_signature = {"K": {"T", "S"}, "B": {"U"}, "D": {"C"}}
        self.assertEqual(objects.rule_c1.create_reactions(atomic_signature, structure_signature),
                         objects.reactions_c1)

        self.assertEqual(objects.rule_no_change.create_reactions(atomic_signature, structure_signature),
                         {objects.reaction_c1_1})

        rule_exp = "K(T{a}).K().K()::cyt => K(T{i}).K().K()::cyt @ k1*[K(T{a}).K().K()::cyt]"
        rule = objects.rule_parser.parse(rule_exp).data[1]
        result = rule.create_reactions(atomic_signature, structure_signature)

        reactions = set()
        with open("Testing/reactions.txt") as file:
            for complex in file.readlines():
                complex = complex.strip()
                rule = objects.rule_parser.parse(complex).data[1]
                reactions.add(rule.to_reaction())

        self.assertEqual(result, reactions)

    def test_compatible(self):
        self.assertTrue(objects.r4.compatible(objects.r5))
        self.assertFalse(objects.r5.compatible(objects.r4))

        rule_expr_1 = "K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
        rule_expr_2 = "K().B()::cyt => K()::cyt + B()::cyt + D(B{_})::cell @ 3*[K()::cyt]/2*v_1"
        rule1 = objects.rule_parser.parse(rule_expr_1).data[1]
        rule2 = objects.rule_parser.parse(rule_expr_2).data[1]

        self.assertFalse(rule1.compatible(rule2))
        self.assertTrue(rule2.compatible(rule1))

    def test_reduce_context(self):
        rule_expr_1 = "K(S{u}).B{i}::cyt => K(S{p})::cyt + B{a}::cyt + D(B{_})::cell @ 3*[K(S{u}).B{i}::cyt]/2*v_1"
        rule1 = objects.rule_parser.parse(rule_expr_1).data[1]

        rule_expr_2 = "K().B{_}::cyt => K()::cyt + B{_}::cyt + D()::cell @ 3*[K().B{_}::cyt]/2*v_1"
        rule2 = objects.rule_parser.parse(rule_expr_2).data[1]

        self.assertEqual(rule1.reduce_context(), rule2)

        # next case

        rule_expr_1 = "K(S{u})::cyt => K(S{p})::cyt + D(B{_})::cell @ 3*[K(S{u})::cyt]/2*v_1"
        rule1 = objects.rule_parser.parse(rule_expr_1).data[1]

        rule_expr_2 = "K()::cyt => K()::cyt + D()::cell @ 3*[K()::cyt]/2*v_1"
        rule2 = objects.rule_parser.parse(rule_expr_2).data[1]

        self.assertEqual(rule1.reduce_context(), rule2)

        # next case - covering replication

        rule_expr_1 = "K(S{u})::cyt => 2 K(S{u})::cyt @ 3*[K(S{u})::cyt]/2*v_1"
        rule1 = objects.rule_parser.parse(rule_expr_1).data[1]

        rule_expr_2 = "K()::cyt => 2 K()::cyt @ 3*[K()::cyt]/2*v_1"
        rule2 = objects.rule_parser.parse(rule_expr_2).data[1]

        self.assertEqual(rule1.reduce_context(), rule2)

        # next case - covering replication

        rule_expr_1 = "K(S{u})::cyt => 3 K(S{u})::cyt @ 3*[K(S{u})::cyt]/2*v_1"
        rule1 = objects.rule_parser.parse(rule_expr_1).data[1]

        rule_expr_2 = "K()::cyt => 3 K()::cyt @ 3*[K()::cyt]/2*v_1"
        rule2 = objects.rule_parser.parse(rule_expr_2).data[1]

        self.assertEqual(rule1.reduce_context(), rule2)

    def test_exists_compatible_agent(self):
        agent = "K(S{a}).A{a}::cyt"
        complex = objects.rate_complex_parser.parse(agent).data.children[0]

        rule_expr = "K().A{i}::cyt => K().A{a}::cyt"
        rule = objects.rule_parser.parse(rule_expr).data[1]

        self.assertTrue(rule.exists_compatible_agent(complex))
