import unittest
import numpy as np
import pandas as pd

from Core.Atomic import AtomicAgent
from Core.Rate import Rate
from Core.Structure import StructureAgent
from Core.Complex import Complex
from Parsing.ParseBCSL import Parser, load_TS_from_json
from TS.Edge import Edge
from TS.State import State
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

        init = State(np.array([2.0, 1.0, 1.0]))

        vector_reactions = {VectorReaction(State(np.array([0.0, 0.0, 0.0])), State(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(State(np.array([1.0, 0.0, 0.0])), State(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(State(np.array([0.0, 0.0, 1.0])), State(np.array([1.0, 0.0, 0.0])), None)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)

        vector_reactions = {VectorReaction(State(np.array([0.0, 0.0, 0.0])), State(np.array([0.0, 1.0, 0.0])), rate_1),
                            VectorReaction(State(np.array([1.0, 0.0, 0.0])), State(np.array([0.0, 0.0, 0.0])), rate_2),
                            VectorReaction(State(np.array([0.0, 0.0, 1.0])), State(np.array([1.0, 0.0, 0.0])), rate_3)}

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
        self.test_ts.states_encoding = {State(np.array((0, 0, 0, 0, 1))): 0,
                                        State(np.array((0, 0, 0, 0, 0))): 1,
                                        State(np.array((0, 0, 1, 0, 0))): 2,
                                        State(np.array((0, 0, 1, 0, 1))): 3,
                                        State(np.array((np.inf, np.inf, np.inf, np.inf, np.inf))): 4,
                                        State(np.array((0, 0, 0, 1, 1))): 5,
                                        State(np.array((0, 0, 1, 1, 1))): 6,
                                        State(np.array((0, 1, 0, 0, 0))): 7,
                                        State(np.array((0, 0, 0, 1, 0))): 8,
                                        State(np.array((0, 0, 1, 1, 0))): 9,
                                        State(np.array((0, 1, 1, 0, 0))): 10,
                                        State(np.array((0, 1, 0, 1, 0))): 11,
                                        State(np.array((0, 1, 1, 1, 0))): 12,
                                        }

        # in edges we have probabilities, not rates, so we must normalise
        go = gamma + omega  # 5
        goa = gamma + omega + alpha  # 15
        goab = gamma + omega + alpha + beta # 20
        gob = gamma + omega + beta  # 10
        oa = omega + alpha  # 13

        self.test_ts.edges = {Edge(0, 1, gamma/go), Edge(0, 3, omega/go),
                              Edge(1, 2, omega/omega),
                              Edge(2, 4, omega/oa), Edge(2, 8, alpha/oa),
                              Edge(3, 2, gamma/goa), Edge(3, 4, omega/goa), Edge(3, 5, alpha/goa),
                              Edge(4, 4, 1),
                              Edge(5, 6, omega/gob), Edge(5, 7, beta/gob), Edge(5, 8, gamma/gob),
                              Edge(6, 4, omega/goab), Edge(6, 4, alpha/goab), Edge(6, 9, gamma/goab), Edge(6, 10, beta/goab),
                              Edge(7, 10, omega/omega),
                              Edge(8, 9, gamma/gamma),
                              Edge(9, 4, omega/oa), Edge(9, 4, alpha/oa),
                              Edge(10, 4, omega/oa), Edge(10, 11, alpha/oa),
                              Edge(11, 12, omega/omega),
                              Edge(12, 4, omega/oa), Edge(12, 4, alpha/oa)
                              }

        # bigger TS

        self.model_bigger_TS = \
            """#! rules
            => K(S{u},T{i})::cyt @ omega
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

    def test_generate_transition_system_interrupt(self):
        # model = self.model_parser.parse(self.model_even_bigger_TS).data
        # vector_model = model.to_vector_model()
        # generated_ts = vector_model.generate_transition_system()
        # generated_ts.save_to_json("Testing/interrupt_even_bigger_ts.json")

        # test not working, after interruption some unprocessed states are missing
        # therefore resulting TS is not correct
        # sometimes edges are somehow mixed - is it possible that the algorithm allows it?
        model = self.model_parser.parse(self.model_even_bigger_TS).data
        vector_model = model.to_vector_model()
        # partially generate TS with max ~1000 states
        generated_ts = vector_model.generate_transition_system(max_size=1000)
        # was interrupted
        generated_ts.save_to_json("Testing/TS_in_progress.json")
        loaded_unfinished_ts = load_TS_from_json("Testing/TS_in_progress.json")

        generated_ts = vector_model.generate_transition_system(loaded_unfinished_ts)
        generated_ts.save_to_json("Testing/TS_finished.json")
        loaded_ts = load_TS_from_json("Testing/interrupt_even_bigger_ts.json")

        # print(len(generated_ts.states_encoding), len(generated_ts.edges), "|",
        #       len(loaded_ts.states_encoding), len(loaded_ts.edges))

        self.assertEqual(generated_ts, loaded_ts)
