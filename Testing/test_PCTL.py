import unittest

from Core.Formula import AtomicProposition
from Parsing.ParseBCSL import Parser
from Parsing.ParsePCTLformula import PCTLparser


class TestPCTL(unittest.TestCase):
    def setUp(self):

        self.parser = PCTLparser()
        self.formula_1 = "P =< 0.3(True U [K(S{i},T{a}).B{o}::cyt => 5])"
        self.formula_2 = "P=?(F [K(S{i},T{a}).B{o}::cyt > 0.33])"

        # parse complex

        self.complex_1 = Parser("rate_complex").parse("K(S{i},T{a}).B{o}::cyt").data.children[0]

        self.ap_1 = AtomicProposition(self.complex_1, " => ", "5")

    def test_parse(self):
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(self.formula_1, str(formula))
        formula = self.parser.parse(self.formula_2)
        self.assertEqual(self.formula_2, str(formula))

    def test_get_complexes(self):
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(formula.get_complexes(), [self.complex_1])

    def test_replace_APs(self):
        replacements = {self.ap_1: "label1"}
        replaced_formula = "P =< 0.3(True U label1)"
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(str(formula.replace_APs(replacements)), replaced_formula)
