import collections
import unittest

from Core.Model import Model
from Regulations.ConcurrentFree import ConcurrentFree
from Regulations.Conditional import Conditional
from Regulations.Ordered import Ordered
from Regulations.Programmed import Programmed
from Parsing.ParseBCSL import Parser
from Regulations.Regular import Regular


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
        self.fail()

    def test_ordered(self):
        regulation = {('r3', 'r1'), ('r1', 'r2')}
        self.model_mini.regulation = Ordered(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.encode(ts.init)
        ts.save_to_json("Testing/regulated_ts.json")
        self.fail()

    def test_conditional(self):
        regulation = {'r3': {self.complex_parser.parse("A(S{a},T{i})::cell").data.children[0]},
                      'r1': set(), 'r2': set()}
        self.model_mini.regulation = Conditional(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.encode(ts.init)
        ts.save_to_json("Testing/regulated_ts.json")
        self.fail()

    def test_concurrent_free(self):
        regulation = {('r3', 'r2')}
        self.model_mini.regulation = ConcurrentFree(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.encode(ts.init)
        ts.save_to_json("Testing/regulated_ts.json")
        self.fail()

    def test_regular(self):
        regulation = ('r1', 'r2')
        self.model_mini.regulation = Regular(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.encode(ts.init)
        ts.save_to_json("Testing/regulated_ts.json")
        self.fail()

    def test_interrupt(self):
        self.fail()

    def test_network_free_simulation_regulated(self):
        regulation = {'r1': {'r2'}}
        self.model_mini.regulation = Programmed(regulation)

        result = self.model_mini.network_free_simulation(5)
        result.to_csv('Testing/regulated_sim.csv', index=None, header=True)
