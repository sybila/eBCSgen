import collections
import unittest

from eBCSgen.Core.Complex import align_agents
import Testing.objects_testing as objects


class TestComplex(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(objects.c8, objects.c10)
        self.assertNotEqual(objects.c8, objects.c11)

    def test_print(self):
        self.assertEqual(str(objects.c8), "X(T{s}).A(S{i},U{a}).A(S{i},U{a})::cyt")
        self.assertEqual(str(objects.c9), "X(T{_}).A(S{i},U{_}).A(S{_},U{a})::cyt")

    def test_compatibility(self):
        self.assertTrue(objects.c9.compatible(objects.c8))
        self.assertFalse(objects.c8.compatible(objects.c9))
        self.assertFalse(objects.c9.compatible(objects.c11))
        self.assertFalse(objects.large_c1.compatible(objects.large_c2))

    def test_to_PRISM_code(self):
        self.assertEqual(objects.c8.to_PRISM_code(5), "VAR_5")

    def test_reduce_context(self):
        self.assertEqual(objects.c12.reduce_context(), objects.c13)

    def test_create_all_compatible(self):
        atomic_signature = {"S": {"a", "i"}, "T": {"u", "p"}}
        structure_signature = {"KaiC": {"S"}}

        complex1 = objects.rate_complex_parser.parse("KaiC(S{a}).T{u}::cyt").data.children[0]
        complex2 = objects.rate_complex_parser.parse("KaiC(S{a}).T{p}::cyt").data.children[0]
        complex3 = objects.rate_complex_parser.parse("KaiC(S{i}).T{u}::cyt").data.children[0]
        complex4 = objects.rate_complex_parser.parse("KaiC(S{i}).T{p}::cyt").data.children[0]
        results_1 = {complex1, complex2, complex3, complex4}
        results_2 = {complex1, complex2}

        complex = objects.rate_complex_parser.parse("KaiC().T{_}::cyt").data.children[0]
        output_comples = complex.create_all_compatible(
            atomic_signature, structure_signature
        )
        self.assertEqual(output_comples, results_1)

        complex = objects.rate_complex_parser.parse("KaiC(S{a}).T{_}::cyt").data.children[0]
        output_comples = complex.create_all_compatible(
            atomic_signature, structure_signature
        )
        self.assertEqual(output_comples, results_2)

        atomic_signature = {"S": {"a", "i"}, "T": {"u", "p"}}
        structure_signature = {"KaiC": {"S", "T"}}

        results = set()
        with open("Testing/complexes_1.txt") as file:
            for complex in file.readlines():
                results.add(objects.rate_complex_parser.parse(complex).data.children[0])

        complex = objects.rate_complex_parser.parse(
            "KaiC().KaiC().KaiC().KaiC().KaiC().KaiC()::cyt"
        ).data.children[0]
        output_comples = complex.create_all_compatible(
            atomic_signature, structure_signature
        )
        self.assertEqual(output_comples, results)

        atomic_signature = {"A": {"+", "-"}, "B": {"HA", "HE"}}
        structure_signature = {"KaiB": {"A", "B"}}

        results = set()
        with open("Testing/complexes_2.txt") as file:
            for complex in file.readlines():
                results.add(objects.rate_complex_parser.parse(complex).data.children[0])

        complex = objects.rate_complex_parser.parse(
            "KaiB().KaiB().KaiB()::cyt"
        ).data.children[0]
        output_comples = complex.create_all_compatible(
            atomic_signature, structure_signature
        )
        self.assertEqual(output_comples, results)

    def test_align_agents(self):
        agent = "X(T{s}).A(S{i},U{a}).A(S{i},U{b})::cyt"
        pattern = "A().A(S{i}).X()::cyt"

        complex = objects.rate_complex_parser.parse(agent).data.children[0]
        pattern = objects.rate_complex_parser.parse(pattern).data.children[0]

        expected_result = {
            (objects.s9, objects.s14, objects.s8),
            (objects.s14, objects.s9, objects.s8),
        }
        result = align_agents(pattern.agents, collections.Counter(complex.agents))
        result = {tuple(item) for item in result}
        self.assertEqual(expected_result, result)
