import unittest

import Core.Formula
import Parsing.ParseBCSL
from Parsing.ParsePCTLformula import PCTLparser


class TestPCTL(unittest.TestCase):
    def setUp(self):

        self.parser = PCTLparser()
        self.formula_1 = "P <= 0.3 [True U K(S{i},T{a}).B{o}::cyt >= 5]"
        self.formula_2 = "P=? [F K(S{i},T{a}).B{o}::cyt > 0.33]"
        self.formula_3 = "P > 0.5 [F K(S{i},T{a}).B{o}::cyt = 2]"

        # parse complex

        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")

        self.complex_1 = complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        self.complex_2 = complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        self.complex_3 = complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]

        self.ap_1 = Core.Formula.AtomicProposition(self.complex_1, " >= ", "5")

    def test_str(self):
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(self.formula_1, str(formula))
        formula = self.parser.parse(self.formula_2)
        self.assertEqual(self.formula_2, str(formula))
        formula = self.parser.parse(self.formula_3)
        self.assertEqual(self.formula_3, str(formula))

    def test_parse(self):
        formula = "P =? [F T(P{m})::x >= 2 & T(P{i})::x = 0]"
        self.assertTrue(self.parser.parse(formula).success)
        formula = "P >= 0.5 [G T(P{m})::x = 2 & T(P{i})::x <= 0]"
        self.assertTrue(self.parser.parse(formula).success)
        formula = "P <= 0.5 [T(P{m})::x < 2 U T(P{m})::x > 0]"
        self.assertTrue(self.parser.parse(formula).success)
        formula = "P > 0.5 [F T(P{m})::x < 2 & ( T(P{m})::x = 0 | T()::x >= 7)]"
        self.assertTrue(self.parser.parse(formula).success)
        formula = "P < 0.5 [G (T(P{m})::x = 2 & T(P{m})::x = 0) | (T(P{m})::x <= 2 & T(P{m})::x >= 0) ]"
        self.assertTrue(self.parser.parse(formula).success)

    def test_get_complexes(self):
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(formula.get_complexes(), [self.complex_1])

    def test_replace_complexes(self):
        labels = {self.complex_1: "VAR_0"}
        replaced_formula = '''P <= 0.3 [True U VAR_0 >= 5]'''
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(str(formula.replace_complexes(labels)), replaced_formula)

    def test_replace_APs(self):
        replacements = {self.ap_1: "property_0"}
        replaced_formula = '''P <= 0.3 [True U \\"property_0\\"]'''
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(str(formula.replace_APs(replacements)), replaced_formula)
