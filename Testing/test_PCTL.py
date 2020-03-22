import unittest

from Core.Formula import AtomicProposition
import Parsing.ParseBCSL
from Parsing.ParsePCTLformula import PCTLparser


class TestPCTL(unittest.TestCase):
    def setUp(self):

        self.parser = PCTLparser()
        self.formula_1 = "P =< 0.3(True U [K(S{i},T{a}).B{o}::cyt => 5])"
        self.formula_2 = "P=?(F [K(S{i},T{a}).B{o}::cyt > 0.33])"

        # parse complex

        complex_parser = Parsing.ParseBCSL.Parser("rate_complex")

        self.complex_1 = complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        self.complex_2 = complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        self.complex_3 = complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]

        self.ap_1 = AtomicProposition(self.complex_1, " => ", "5")

    def test_parse(self):
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(self.formula_1, str(formula))
        formula = self.parser.parse(self.formula_2)
        self.assertEqual(self.formula_2, str(formula))

    def test_replace_complexes(self):
        ordering = (self.complex_1, self.complex_2, self.complex_3)
        replaced_formula = "P =< 0.3(True U [VAR_0 => 5])"
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(str(formula.replace_complexes(ordering)), replaced_formula)

    def test_replace_APs(self):
        replacements = {self.ap_1: "label1"}
        replaced_formula = "P =< 0.3(True U label1)"
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(str(formula.replace_APs(replacements)), replaced_formula)
