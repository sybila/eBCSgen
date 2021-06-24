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
        self.complex_parser = Parser("rate_complex")

        self.model_with_labels = """
            #! rules
            r1_S ~ A(S{i})::cell => A(S{a})::cell @ k1*[A(S{i})::cell]
            r1_T ~ A(T{i})::cell => A(T{a})::cell @ k2*[A(T{i})::cell]
            r2 ~ A()::cell => A()::out @ k3*[A()::cell]

            #! inits
            1 A(S{i},T{i})::cell

            #! definitions
            k1 = 0.3
            k2 = 0.5
            k3 = 0.1
            """

        self.model_mini = self.model_parser.parse(self.model_with_labels).data

    def test_programmed(self):
        regulation = {'r1_S': {'r1_T', 'r2'}, 'r1_T': {'r1_S'}}
        self.model_mini.regulation = Programmed(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.export("Testing/regulations/programmed_ts.json")

    def test_ordered(self):
        regulation = {('r1_S', 'r2'), ('r1_T', 'r2')}
        self.model_mini.regulation = Ordered(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.export("Testing/regulations/ordered_ts.json")

    def test_conditional(self):
        regulation = {'r2': {self.complex_parser.parse("A(S{a},T{i})::cell").data.children[0]},
                      'r1_S': set(), 'r1_T': set()}
        self.model_mini.regulation = Conditional(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.export("Testing/regulations/conditional_ts.json")

    def test_concurrent_free(self):
        regulation = {('r1_S', 'r2'), ('r1_T', 'r2')}
        self.model_mini.regulation = ConcurrentFree(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.export("Testing/regulations/concurrent_free_ts.json")

    def test_regular(self):
        regulation = r'(r1_Sr1_Tr2|r1_Tr1_Sr2)'
        self.model_mini.regulation = Regular(regulation)

        ts = self.model_mini.generate_direct_transition_system()
        ts.export("Testing/regulations/regular_ts.json")

    def test_no_regulation(self):
        ts = self.model_mini.generate_direct_transition_system()
        ts.export("Testing/regulations/no_regulation_ts.json")

    def test_network_free_simulation_regulated(self):
        regulation = {'r1_S': {'r1_T'}, 'r1_T': {'r2'}}
        self.model_mini.regulation = Programmed(regulation)

        result = self.model_mini.network_free_simulation(5)
        result.to_csv('Testing/regulated_sim.csv', index=None, header=True)
