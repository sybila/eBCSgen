import collections
import unittest

import Parsing.ParseBCSL
from Core.Structure import StructureAgent
from Core.Atomic import AtomicAgent
from Core.Complex import Complex, align_agents


class TestComplex(unittest.TestCase):
    def setUp(self):
        self.a1 = AtomicAgent("T", "s")
        self.a2 = AtomicAgent("S", "i")
        self.a3 = AtomicAgent("U", "a")
        self.a4 = AtomicAgent("T", "_")
        self.a5 = AtomicAgent("U", "_")
        self.a6 = AtomicAgent("S", "_")
        self.a7 = AtomicAgent("U", "b")

        self.s1 = StructureAgent("X", {self.a1})
        self.s2 = StructureAgent("A", {self.a2, self.a3})
        self.s3 = StructureAgent("X", {self.a4})
        self.s4 = StructureAgent("A", {self.a2, self.a5})
        self.s5 = StructureAgent("A", {self.a6, self.a3})
        self.s6 = StructureAgent("A", set())
        self.s7 = StructureAgent("A", {self.a2, self.a7})

        self.c1 = Complex([self.s1, self.s2, self.s2], "cyt")
        self.c2 = Complex([self.s3, self.s4, self.s5], "cyt")
        self.c3 = Complex([self.s2, self.s2, self.s1], "cyt")
        self.c4 = Complex([self.s2, self.s2, self.s1], "cell")

        self.c5 = Complex([self.s2, self.s4, self.a1], "cell")
        self.c6 = Complex([self.s6, self.s6, self.a4], "cell")

        self.large_c1 = Complex([self.s4] * 6 + [self.s3] * 5, "cell")
        self.large_c2 = Complex([self.s5] * 7 + [self.s3] * 6, "cell")

    def test_eq(self):
        self.assertEqual(self.c1, self.c3)
        self.assertNotEqual(self.c1, self.c4)

    def test_print(self):
        self.assertEqual(str(self.c1), "X(T{s}).A(S{i},U{a}).A(S{i},U{a})::cyt")
        self.assertEqual(str(self.c2), "X(T{_}).A(S{i},U{_}).A(S{_},U{a})::cyt")

    def test_compatibility(self):
        self.assertTrue(self.c2.compatible(self.c1))
        self.assertFalse(self.c1.compatible(self.c2))
        self.assertFalse(self.c2.compatible(self.c4))
        self.assertFalse(self.large_c1.compatible(self.large_c2))

    def test_to_PRISM_code(self):
        self.assertEqual(self.c1.to_PRISM_code(5), "VAR_5")

    def test_reduce_context(self):
        self.assertEqual(self.c5.reduce_context(), self.c6)

    def test_create_all_compatible(self):
        atomic_signature = {"S": {"a", "i"}, "T": {"u", "p"}}
        structure_signature = {"KaiC": {"S"}}

        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")

        complex1 = complex_parser.parse("KaiC(S{a}).T{u}::cyt").data.children[0]
        complex2 = complex_parser.parse("KaiC(S{a}).T{p}::cyt").data.children[0]
        complex3 = complex_parser.parse("KaiC(S{i}).T{u}::cyt").data.children[0]
        complex4 = complex_parser.parse("KaiC(S{i}).T{p}::cyt").data.children[0]
        results_1 = {complex1, complex2, complex3, complex4}
        results_2 = {complex1, complex2}

        complex = complex_parser.parse("KaiC().T{_}::cyt").data.children[0]
        output_comples = complex.create_all_compatible(atomic_signature, structure_signature)
        self.assertEqual(output_comples, results_1)

        complex = complex_parser.parse("KaiC(S{a}).T{_}::cyt").data.children[0]
        output_comples = complex.create_all_compatible(atomic_signature, structure_signature)
        self.assertEqual(output_comples, results_2)

        atomic_signature = {"S": {"a", "i"}, "T": {"u", "p"}}
        structure_signature = {"KaiC": {"S", "T"}}

        results = set()
        with open("Testing/complexes_1.txt") as file:
            for complex in file.readlines():
                results.add(complex_parser.parse(complex).data.children[0])

        complex = complex_parser.parse("KaiC().KaiC().KaiC().KaiC().KaiC().KaiC()::cyt").data.children[0]
        output_comples = complex.create_all_compatible(atomic_signature, structure_signature)
        self.assertEqual(output_comples, results)

        atomic_signature = {"A": {"+", "-"}, "B": {"HA", "HE"}}
        structure_signature = {"KaiB": {"A", "B"}}

        results = set()
        with open("Testing/complexes_2.txt") as file:
            for complex in file.readlines():
                results.add(complex_parser.parse(complex).data.children[0])

        complex = complex_parser.parse("KaiB().KaiB().KaiB()::cyt").data.children[0]
        output_comples = complex.create_all_compatible(atomic_signature, structure_signature)
        self.assertEqual(output_comples, results)

    def test_align_agents(self):
        agent = "X(T{s}).A(S{i},U{a}).A(S{i},U{b})::cyt"
        pattern = "A().A(S{i}).X()::cyt"

        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")

        complex = complex_parser.parse(agent).data.children[0]
        pattern = complex_parser.parse(pattern).data.children[0]

        expected_result = {(self.s2, self.s7, self.s1), (self.s7, self.s2, self.s1)}
        result = align_agents(pattern.agents, collections.Counter(complex.agents))
        result = {tuple(item) for item in result}
        self.assertEqual(expected_result, result)
