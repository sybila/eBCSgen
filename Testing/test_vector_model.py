import unittest
import numpy as np
import pandas as pd

from Core.Atomic import AtomicAgent
from Core.Rate import Rate
from Core.Structure import StructureAgent
from Core.Complex import Complex
from Parsing.ParseBCSL import Parser, load_TS_from_json
from TS.Edge import Edge
from TS.State import MemorylessState
from TS.TransitionSystem import TransitionSystem
from TS.VectorModel import VectorModel
from TS.VectorReaction import VectorReaction


class TestVectorModel(unittest.TestCase):
    def setUp(self):
        self.s1 = StructureAgent("X", set())
        self.s2 = StructureAgent("Y", set())
        self.s3 = StructureAgent("Z", set())

        self.c1 = Complex([self.s1], "rep")
        self.c2 = Complex([self.s2], "rep")
        self.c3 = Complex([self.s3], "rep")

        ordering = (self.c1, self.c2, self.c3)
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

        init = MemorylessState(np.array([2.0, 1.0, 1.0]))

        vector_reactions = {VectorReaction(MemorylessState(np.array([0.0, 0.0, 0.0])), MemorylessState(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(MemorylessState(np.array([1.0, 0.0, 0.0])), MemorylessState(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(MemorylessState(np.array([0.0, 0.0, 1.0])), MemorylessState(np.array([1.0, 0.0, 0.0])), None)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)

        vector_reactions = {VectorReaction(MemorylessState(np.array([0.0, 0.0, 0.0])), MemorylessState(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(MemorylessState(np.array([1.0, 0.0, 0.0])), MemorylessState(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(MemorylessState(np.array([0.0, 0.0, 1.0])), MemorylessState(np.array([1.0, 0.0, 0.0])), rate_3)}

        self.vm_2 = VectorModel(vector_reactions, init, ordering, None)

        # test abstract model

        self.model_parser = Parser("model")

        self.model_abstract = \
            """#! rules
            => X()::rep @ k2*[T{_}::rep]
            T{a}::rep => T{i}::rep @ k1*[T{_}::rep]

            #! inits
            10 T{a}::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

        # test transition system generating

        a1 = AtomicAgent("B", "a")
        a2 = AtomicAgent("S", "u")
        a3 = AtomicAgent("S", "p")
        a4 = AtomicAgent("T", "i")

        s1 = StructureAgent("K", {a3, a4})
        s2 = StructureAgent("K", {a2, a4})

        cx1 = Complex([a1], "cyt")
        cx2 = Complex([s1], "cyt")
        cx3 = Complex([s2], "cyt")
        cx4 = Complex([s1, a1], "cyt")
        cx5 = Complex([s2, a1], "cyt")

        ordering = (cx5, cx4, cx3, cx2, cx1)
        # (K(S{u},T{i}).B{a}::cyt, K(S{p},T{i}).B{a}::cyt, K(S{u},T{i})::cyt, K(S{p},T{i})::cyt, B{a}::cyt)

        self.model_TS = \
            """#! rules
            => K(S{u},T{i})::cyt @ omega
            K(S{u})::cyt => K(S{p})::cyt @ alpha*[K(S{u})::cyt]
            K(S{p})::cyt + B{a}::cyt => K(S{p}).B{a}::cyt @ beta*[K(S{p})::cyt]*[B{a}::cyt]
            B{_}::cyt => @ gamma*[B{_}::cyt]
            K(S{u},T{i}).B{a}::cyt => @ 5

            #! inits
            1 B{a}::cyt

            #! definitions
            alpha = 10
            beta = 5
            gamma = 2
            omega = 3
            """

        alpha = 10
        beta = 5
        gamma = 2
        omega = 3

        self.test_ts = TransitionSystem(ordering)

        states = [MemorylessState(np.array((0.0, 0.0, 0.0, 0.0, 1.0))),
                  MemorylessState(np.array((0.0, 0.0, 0.0, 0.0, 0.0))),
                  MemorylessState(np.array((0.0, 0.0, 1.0, 0.0, 0.0))),
                  MemorylessState(np.array((0.0, 0.0, 1.0, 0.0, 1.0))),
                  MemorylessState(np.array((np.inf, np.inf, np.inf, np.inf, np.inf))),
                  MemorylessState(np.array((0.0, 0.0, 0.0, 1.0, 1.0))),
                  MemorylessState(np.array((0.0, 0.0, 1.0, 1.0, 1.0))),
                  MemorylessState(np.array((0.0, 1.0, 0.0, 0.0, 0.0))),
                  MemorylessState(np.array((0.0, 0.0, 0.0, 1.0, 0.0))),
                  MemorylessState(np.array((0.0, 0.0, 1.0, 1.0, 0.0))),
                  MemorylessState(np.array((0.0, 1.0, 1.0, 0.0, 0.0))),
                  MemorylessState(np.array((0.0, 1.0, 0.0, 1.0, 0.0))),
                  MemorylessState(np.array((0.0, 1.0, 1.0, 1.0, 0.0)))]

        # in edges we have probabilities, not rates, so we must normalise
        go = gamma + omega  # 5
        goa = gamma + omega + alpha  # 15
        goab = gamma + omega + alpha + beta  # 20
        gob = gamma + omega + beta  # 10
        oa = omega + alpha  # 13

        self.test_ts.processed = set(states)

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

        self.test_ts.encode(states[0])

        # bigger TS

        self.model_bigger_TS = \
            """#! rules
            => 2 K(S{u},T{i})::cyt @ omega
            K(S{u})::cyt => K(S{p})::cyt @ alpha*[K(S{u})::cyt]
            K(S{p})::cyt + B{a}::cyt => K(S{p}).B{a}::cyt @ beta*[K(S{p})::cyt]*[B{a}::cyt]
            B{_}::cyt => @ gamma*[B{_}::cyt]
            K(S{u},T{i}).B{a}::cyt => @ 5

            #! inits
            6 B{a}::cyt

            #! definitions
            alpha = 10
            beta = 5
            gamma = 2
            omega = 3
            """

        # even bigger TS

        self.model_even_bigger_TS = \
            """#! rules
            => K(S{u},T{i})::cyt @ omega
            K(S{u})::cyt => K(S{p})::cyt @ alpha*[K(S{u})::cyt]
            K(S{p})::cyt + B{a}::cyt => K(S{p}).B{a}::cyt @ beta*[K(S{p})::cyt]*[B{a}::cyt]
            B{_}::cyt => @ gamma*[B{_}::cyt]
            K(S{u},T{i}).B{a}::cyt => @ 5

            #! inits
            10 B{a}::cyt

            #! definitions
            alpha = 10
            beta = 5
            gamma = 2
            omega = 3
            """

        self.model_parametrised = \
            """#! rules
            => K(S{u},T{i})::cyt @ omega
            K(S{u})::cyt => K(S{p})::cyt @ alpha*[K(S{u})::cyt]
            K(S{p})::cyt + B{a}::cyt => K(S{p}).B{a}::cyt @ beta*[K(S{p})::cyt]*[B{a}::cyt]
            B{_}::cyt => @ gamma*[B{_}::cyt]
            K(S{u},T{i}).B{a}::cyt => @ 5

            #! inits
            1 B{a}::cyt

            #! definitions
            alpha = 10
            beta = 5
            //gamma = 2
            omega = 3
            """

        self.model_with_sinks = \
            """#! rules
            K(S{u})::cyt => K(S{p})::cyt @ alpha*[K(S{u})::cyt]
            K(S{p})::cyt + B{a}::cyt => K(S{p}).B{a}::cyt @ beta*[K(S{p})::cyt]*[B{a}::cyt]
            B{a}::cyt => B{i}::cyt @ alpha*[B{_}::cyt]

            #! inits
            1 B{a}::cyt
            1 K(S{u})::cyt

            #! definitions
            alpha = 10
            beta = 5
            """

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

        # to save dataframe to csv file
        # data_simulated.to_csv("Testing/stochastic_out.csv", index=None, header=True)

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
