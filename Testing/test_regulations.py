import unittest

from eBCSgen.Parsing.ParseBCSL import Parser


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

    def test_programmed(self):
        regulation = """

        #! regulation
        type programmed
        r1_S: {r1_T, r2}
        r1_T: {r1_S}
        """
        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_ordered(self):
        regulation = """

        #! regulation
        type ordered
        (r1_S, r2), (r1_T, r2)
        """

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_conditional(self):
        regulation = """

        #! regulation
        type conditional
        r2: {A(S{a},T{i})::cell}
        """

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_concurrent_free(self):
        regulation = """

        #! regulation
        type concurrent-free
        (r1_S, r2), (r1_T, r2)
        """

        model = self.model_parser.parse(self.model_with_labels + regulation).data

        direct_ts = model.generate_direct_transition_system()
        direct_ts.change_to_vector_backend()

        vm = model.to_vector_model()
        indirect_ts = vm.generate_transition_system()

        self.assertEqual(direct_ts, indirect_ts)

    def test_regular(self):
        regulation = """

        #! regulation
        type regular
        (r1_Sr1_Tr2|r1_Tr1_Sr2)
        """

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
        regulation = """

        #! regulation
        type programmed
        r1_S: {r1_T, r2}
        r1_T: {r1_S}
        """
        model = self.model_parser.parse(self.model_with_labels + regulation).data

        result = model.network_free_simulation(5)
        result.to_csv('Testing/regulated_sim.csv', index=None, header=True)
