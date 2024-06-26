import unittest
import numpy as np
import pandas as pd

from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Rate import Rate
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Parsing.ParseBCSL import Parser, load_TS_from_json
from eBCSgen.TS.Edge import Edge
from eBCSgen.TS.State import State, Vector, Memory
from eBCSgen.TS.TransitionSystem import TransitionSystem
from eBCSgen.TS.VectorModel import VectorModel
from eBCSgen.TS.VectorReaction import VectorReaction

import Testing.objects_testing as objects
from Testing.models.get_model_str import get_model_str


class TestVectorModel(unittest.TestCase):
    def setUp(self):

        ordering = (objects.c27, objects.c28, objects.c29)
        params = {"k1": 0.05, "k2": 0.1}

        self.rate_parser = Parser("rate")
        rate_expr = "1/(1+([X()::rep])**2)"
        rate_1 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_1.vectorize(ordering, params)

        rate_expr = "k1*[X()::rep]"
        rate_2 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_2.vectorize(ordering, params)

        rate_expr = "k2*[Z()::rep]"
        rate_3 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_3.vectorize(ordering, params)

        init = State(Vector(np.array([2.0, 1.0, 1.0])), Memory(0))

        vector_reactions = {VectorReaction(State(Vector(np.array([0.0, 0.0, 0.0])), Memory(0)),
                                           State(Vector(np.array([0.0, 1.0, 0.0])), Memory(0)),
                                           rate_1),
                            VectorReaction(State(Vector(np.array([1.0, 0.0, 0.0])), Memory(0)),
                                           State(Vector(np.array([0.0, 0.0, 0.0])), Memory(0)),
                                           rate_2),
                            VectorReaction(State(Vector(np.array([0.0, 0.0, 1.0])), Memory(0)),
                                           State(Vector(np.array([1.0, 0.0, 0.0])), Memory(0)),
                                           None)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)

        vector_reactions = {VectorReaction(State(Vector(np.array([0.0, 0.0, 0.0])), Memory(0)),
                                           State(Vector(np.array([0.0, 1.0, 0.0])), Memory(0)),
                                           rate_1),
                            VectorReaction(State(Vector(np.array([1.0, 0.0, 0.0])), Memory(0)),
                                           State(Vector(np.array([0.0, 0.0, 0.0])), Memory(0)),
                                           rate_2),
                            VectorReaction(State(Vector(np.array([0.0, 0.0, 1.0])), Memory(0)),
                                           State(Vector(np.array([1.0, 0.0, 0.0])), Memory(0)),
                                           rate_3)}

        self.vm_2 = VectorModel(vector_reactions, init, ordering, None)

        # test abstract model

        self.model_parser = Parser("model")

        self.model_abstract = get_model_str("model_abstract")

        # test transition system generating

        ordering = (objects.cx5, objects.cx4, objects.cx3, objects.cx2, objects.cx1)
        # (K(S{u},T{i}).B{a}::cyt, K(S{p},T{i}).B{a}::cyt, K(S{u},T{i})::cyt, K(S{p},T{i})::cyt, B{a}::cyt)

        self.model_TS = get_model_str("model_TS")

        alpha = 10
        beta = 5
        gamma = 2
        omega = 3

        self.test_ts = TransitionSystem(ordering, 2)

        states = [State(Vector(np.array((0.0, 0.0, 0.0, 0.0, 1.0))), Memory(0)),
                  State(Vector(np.array((0.0, 0.0, 0.0, 0.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 0.0, 1.0, 0.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 0.0, 1.0, 0.0, 1.0))), Memory(0)),
                  State(Vector(np.array((np.inf, np.inf, np.inf, np.inf, np.inf))), Memory(0), True),
                  State(Vector(np.array((0.0, 0.0, 0.0, 1.0, 1.0))), Memory(0)),
                  State(Vector(np.array((0.0, 0.0, 1.0, 1.0, 1.0))), Memory(0)),
                  State(Vector(np.array((0.0, 1.0, 0.0, 0.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 0.0, 0.0, 1.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 0.0, 1.0, 1.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 1.0, 1.0, 0.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 1.0, 0.0, 1.0, 0.0))), Memory(0)),
                  State(Vector(np.array((0.0, 1.0, 1.0, 1.0, 0.0))), Memory(0))]

        # in edges we have probabilities, not rates, so we must normalise
        go = gamma + omega  # 5
        goa = gamma + omega + alpha  # 15
        goab = gamma + omega + alpha + beta  # 20
        gob = gamma + omega + beta  # 10
        oa = omega + alpha  # 13

        self.test_ts.states = set(states)

        self.test_ts.edges = {Edge(states[0], states[1], gamma / go), Edge(states[0], states[3], omega / go),
                              Edge(states[1], states[2], omega / omega),
                              Edge(states[2], states[4], omega / oa), Edge(states[2], states[8], alpha / oa),
                              Edge(states[3], states[2], gamma / goa), Edge(states[3], states[4], omega / goa),
                              Edge(states[3], states[5], alpha / goa),
                              Edge(states[4], states[4], 1),
                              Edge(states[5], states[6], omega / gob), Edge(states[5], states[7], beta / gob),
                              Edge(states[5], states[8], gamma / gob),
                              Edge(states[6], states[4], oa / goab),
                              Edge(states[6], states[9], gamma / goab), Edge(states[6], states[10], beta / goab),
                              Edge(states[7], states[10], omega / omega),
                              Edge(states[8], states[9], gamma / gamma),
                              Edge(states[9], states[4], 1),
                              Edge(states[10], states[4], omega / oa), Edge(states[10], states[11], alpha / oa),
                              Edge(states[11], states[12], omega / omega),
                              Edge(states[12], states[4], 1)
                              }

        self.test_ts.init = states[0]
        self.test_ts.encode()

        # bigger TS

        self.model_bigger_TS = get_model_str("model_bigger_TS")

        # even bigger TS

        self.model_even_bigger_TS = get_model_str("model_even_bigger_TS")

        self.model_parametrised = get_model_str("model_parametrised2")

        self.model_with_sinks = get_model_str("model_with_sinks")

    def test_compute_bound(self):
        self.assertEqual(self.vm_1.bound, 2)

    def test_deterministic_simulation(self):
        # simple rates
        data_simulated = self.vm_2.deterministic_simulation(3, 1/(6.022 * 10**23))
        data_loaded = pd.read_csv("Testing/simple_out.csv")

        pd.testing.assert_frame_equal(data_simulated, data_loaded)

        # more abstract rates

        model = self.model_parser.parse(self.model_abstract).data
        vector_model = model.to_vector_model()
        data_simulated = vector_model.deterministic_simulation(3, 1/(6.022 * 10**23))
        data_loaded = pd.read_csv("Testing/abstract_out.csv")

        pd.testing.assert_frame_equal(data_simulated, data_loaded)

    def test_stochastic_simulation(self):
        model = self.model_parser.parse(self.model_abstract).data
        vector_model = model.to_vector_model()

        data_simulated = vector_model.stochastic_simulation(5, 4, testing=True)
        data_loaded = pd.read_csv("Testing/stochastic_out.csv")
        pd.testing.assert_frame_equal(data_simulated, data_loaded)

    def test_generate_transition_system(self):
        model = self.model_parser.parse(self.model_TS).data
        vector_model = model.to_vector_model()
        generated_ts = vector_model.generate_transition_system()
        self.assertEqual(self.test_ts, generated_ts)

        # bigger TS

        model = self.model_parser.parse(self.model_bigger_TS).data
        vector_model = model.to_vector_model()
        generated_ts = vector_model.generate_transition_system()
        loaded_ts = load_TS_from_json("Testing/testing_bigger_ts.json")
        self.assertEqual(generated_ts, loaded_ts)

    def test_save_to_json(self):
        model = self.model_parser.parse(self.model_TS).data
        vector_model = model.to_vector_model()
        generated_ts = vector_model.generate_transition_system()
        generated_ts.save_to_json("Testing/testing_ts.json")
        loaded_ts = load_TS_from_json("Testing/testing_ts.json")
        self.assertEqual(generated_ts, loaded_ts)

    def test_generate_pMC(self):
        model = self.model_parser.parse(self.model_parametrised).data
        vector_model = model.to_vector_model()
        generated_ts = vector_model.generate_transition_system()
        loaded_ts = load_TS_from_json("Testing/ts_pMC.json")
        self.assertEqual(generated_ts, loaded_ts)

    def test_generate_transition_system_interrupt(self):
        model = self.model_parser.parse(self.model_even_bigger_TS).data
        vector_model = model.to_vector_model()

        # partially generate TS with max ~1000 states
        generated_ts = vector_model.generate_transition_system(max_size=1000)
        # was interrupted
        generated_ts.save_to_json("Testing/TS_in_progress.json")
        loaded_unfinished_ts = load_TS_from_json("Testing/TS_in_progress.json")

        # continue in generating with max ~5000 states
        generated_ts = vector_model.generate_transition_system(loaded_unfinished_ts, max_size=5000)
        generated_ts.save_to_json("Testing/TS_in_progress.json")
        loaded_unfinished_ts = load_TS_from_json("Testing/TS_in_progress.json")

        # finish the TS
        generated_ts = vector_model.generate_transition_system(loaded_unfinished_ts)

        generated_ts.save_to_json("Testing/TS_finished.json")
        loaded_ts = load_TS_from_json("Testing/interrupt_even_bigger_ts.json")

        self.assertEqual(generated_ts, loaded_ts)

    def test_handle_sinks(self):
        model = self.model_parser.parse(self.model_with_sinks).data
        vector_model = model.to_vector_model()
        generated_ts = vector_model.generate_transition_system()
        loaded_ts = load_TS_from_json("Testing/TS_with_sinks.json")
        self.assertEqual(generated_ts, loaded_ts)
