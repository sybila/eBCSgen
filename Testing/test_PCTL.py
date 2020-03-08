import unittest

from Parsing.ParsePCTLformula import PCTLparser


class TestPCTL(unittest.TestCase):
    def setUp(self):

        self.parser = PCTLparser()
        self.formula_1 = "P =< 0.3(True U [K(S{i},T{a}).B{o}::cyt => 5])"

    def test_parse(self):
        formula = self.parser.parse(self.formula_1)
        self.assertEqual(self.formula_1, str(formula))
