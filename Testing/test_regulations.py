import unittest

from eBCSgen.Parsing.ParseBCSL import Parser
from Testing.models.get_model_str import get_model_str


class TestRegulations(unittest.TestCase):
    def setUp(self):
        self.model_parser = Parser("model")
        self.complex_parser = Parser("rate_complex")

        self.model_with_labels = get_model_str("model_with_labels")

    def test_programmed(self):
        regulation = get_model_str("regulation1")
        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_ordered(self):
        regulation = get_model_str("regulation2")

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_conditional(self):
        regulation = get_model_str("regulation3")

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_concurrent_free(self):
        regulation = get_model_str("regulation4")

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_regular(self):
        regulation = get_model_str("regulation5")

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_no_regulation(self):
        model = self.model_parser.parse(self.model_with_labels).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_network_free_simulation_regulated(self):
        regulation = get_model_str("regulation1")
        model = self.model_parser.parse(self.model_with_labels + regulation).data

        result = model.network_free_simulation(5)
        result.to_csv('Testing/regulated_sim.csv', index=None, header=True)
