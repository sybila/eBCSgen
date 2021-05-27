import collections
import unittest

from Core.Model import Model
from Core.Regulations.Programmed import Programmed
from Parsing.ParseBCSL import Parser


class TestRegulations(unittest.TestCase):
    def setUp(self):
        self.model_parser = Parser("model")
        self.rule_parser = Parser("rule")
        self.complex_parser = Parser("rate_complex")

        init_complex = self.complex_parser.parse("A(S{i},T{i})::cell").data.children[0]
        init = collections.Counter([init_complex])

        rule_exp = "A(S{i})::cell => A(S{a})::cell @ k1*[A(S{i})::cell]"
        rule_1 = self.rule_parser.parse(rule_exp).data
        rule_1.label = "r1"

        rule_exp = "A(S{a})::cell => A(S{a})::cyt @ k2*[A(S{a})::cell]"
        rule_2 = self.rule_parser.parse(rule_exp).data
        rule_2.label = "r2"

        rule_exp = "A(S{a},T{i})::cell => A(S{a},T{a})::cell @ k3*[A(T{i})::cell]"
        rule_3 = self.rule_parser.parse(rule_exp).data
        rule_3.label = "r3"

        self.model_mini = Model({rule_1, rule_2, rule_3}, init, {'k1': 0.3, 'k2': 0.5, 'k3': 0.1}, set())

    def test_programmed(self):
        regulation = {'r1': {'r2'}}
        self.model_mini.regulation = Programmed(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.encode(ts.init)
        ts.save_to_json("Testing/regulated_ts.json")
