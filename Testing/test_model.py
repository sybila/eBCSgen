import unittest
import collections
import sortedcontainers
import numpy as np

from Core.Model import Model
from Core.Rate import Rate
from Core.Structure import StructureAgent
from Core.Complex import Complex
from Core.Rule import Rule
from Parsing.ParseBCSL import Parser
from TS.State import MemorylessState
import TS.TransitionSystem
from TS.VectorModel import VectorModel
from TS.VectorReaction import VectorReaction
import Core.Formula


class TestModel(unittest.TestCase):
    def setUp(self):
        # agents

        self.s1 = StructureAgent("X", set())
        self.s2 = StructureAgent("Y", set())
        self.s3 = StructureAgent("Z", set())

        self.c1 = Complex([self.s1], "rep")
        self.c2 = Complex([self.s2], "rep")
        self.c3 = Complex([self.s3], "rep")

        #  rules

        sequence_1 = (self.s1,)
        mid_1 = 1
        compartments_1 = ["rep"]
        complexes_1 = [(0, 0)]
        pairs_1 = [(0, None)]
        rate_1 = Rate("k1*[X()::rep]")

        self.r1 = Rule(sequence_1, mid_1, compartments_1, complexes_1, pairs_1, rate_1)

        sequence_2 = (self.s3, self.s1)
        mid_2 = 1
        compartments_2 = ["rep"] * 2
        complexes_2 = [(0, 0), (1, 1)]
        pairs_2 = [(0, 1)]

        self.r2 = Rule(sequence_2, mid_2, compartments_2, complexes_2, pairs_2, None)

        sequence_3 = (self.s2,)
        mid_3 = 0
        compartments_3 = ["rep"]
        complexes_3 = [(0, 0)]
        pairs_3 = [(None, 0)]
        rate_3 = Rate("1.0/(1.0+([X()::rep])**4.0)")

        self.r3 = Rule(sequence_3, mid_3, compartments_3, complexes_3, pairs_3, rate_3)

        # inits

        self.inits = collections.Counter({self.c1: 2, self.c2: 1})

        # defs

        self.defs = {'k1': 0.05, 'k2': 0.12}

        self.model = Model({self.r1, self.r2, self.r3}, self.inits, self.defs, set())
        # model

        self.model_str_1 = """
        #! rules
        X()::rep => @ k1*[X()::rep]
        Z()::rep => X()::rep
        => Y()::rep @ 1/(1+([X()::rep])**4)

        #! inits
        2 X()::rep
        Y()::rep
        
        #! definitions
        k1 = 0.05
        k2 = 0.12   
        """

        self.model_parser = Parser("model")

        self.model_str_2 = """
        #! rules
        X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
        X(T{a})::rep => X(T{o})::rep @ k2*[Z()::rep]
        => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

        #! inits
        2 X(K{c}, T{e}).X(K{c}, T{j})::rep
        Y(P{g}, N{l})::rep

        #! definitions
        k1 = 0.05
        k2 = 0.12
        """

        # vectors

        ordering = (self.c1, self.c2, self.c3)

        self.rate_parser = Parser("rate")
        rate_expr = "1/(1+([X()::rep])**4)"
        rate_1 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_1.vectorize(ordering, dict())

        rate_expr = "k1*[X()::rep]"
        rate_2 = Rate(self.rate_parser.parse(rate_expr).data)
        rate_2.vectorize(ordering, {"k1": 0.05})

        init = MemorylessState(np.array([2, 1, 0]))

        vector_reactions = {VectorReaction(MemorylessState(np.array([0, 0, 0])), MemorylessState(np.array([0, 1, 0])), rate_1),
                            VectorReaction(MemorylessState(np.array([1, 0, 0])), MemorylessState(np.array([0, 0, 0])), rate_2),
                            VectorReaction(MemorylessState(np.array([0, 0, 1])), MemorylessState(np.array([1, 0, 0])), None)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)

        # wrong models

        self.model_wrong_1 = \
            """#! rules
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
            X(T{a})::rep => X(T{o}):;rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

        self.model_wrong_2 = \
            """#! rules
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep]
            X(T{a})::rep = X(T{o})::rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(1+([X()::rep])**4)

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep

            #! definitions
            k1 = 0.05
            k2 = 0.12
            """

        self.model_with_comments = """
            #! rules
            // commenting
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep] // also here
            X(T{a})::rep => X(T{o})::rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(1+([X()::rep])**4) // ** means power (^)

            #! inits
            // here
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep // comment just 1 item

            #! definitions
            // and
            k1 = 0.05 // also
            k2 = 0.12
            """
        
        self.model_with_complexes = """
            #! rules
            // commenting
            X(T{a}):XX::rep => X(T{o}):XX::rep @ k2*[X().X()::rep]
            K{i}:X():XYZ::rep => K{p}:X():XYZ::rep @ k1*[X().Y().Z()::rep] // also here
            => P{f}:XP::rep @ 1/(1+([X().P{_}::rep])**4) // ** means power (^)

            #! inits
            // here
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep // comment just 1 item

            #! definitions
            // and
            k1 = 0.05 // also
            k2 = 0.12

            #! complexes
            XYZ = X().Y().Z() // a big complex
            XX = X().X()
            XP = X().P{_}
            """

        self.model_without_complexes = """
            #! rules
            // commenting
            X(T{a}).X()::rep => X(T{o}).X()::rep @ k2*[X().X()::rep]
            X(K{i}).Y().Z()::rep => X(K{p}).Y().Z()::rep @ k1*[X().Y().Z()::rep] // also here
            => X().P{f}::rep @ 1/(1+([X().P{_}::rep])**4) // ** means power (^)

            #! inits
            // here
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep // comment just 1 item

            #! definitions
            // and
            k1 = 0.05 // also
            k2 = 0.12
            """

        self.model_with_variable = """
            #! rules
            // commenting
            T{a}:X():?::rep => T{o}:X():?::rep @ k2*[X().X()::rep] ; ? = { XX, XY }
            K{i}:X():XY::rep => K{p}:X():XY::rep @ k1*[X().Y().Z().X()::rep] // also here

            #! inits
            // here
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep

            #! definitions
            // and
            k1 = 0.05 // also
            k2 = 0.12

            #! complexes
            XX = X().X()
            XY = X().Y()
            """

        self.model_without_variable = """
            #! rules
            // commenting
            X(K{i}).Y()::rep => X(K{p}).Y()::rep @ k1*[X().Y().Z().X()::rep]
            X(T{a}).X()::rep => X(T{o}).X()::rep @ k2*[X().X()::rep]
            X(T{a}).Y()::rep => X(T{o}).Y()::rep @ k2*[X().X()::rep]

            #! inits
            // here
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep

            #! definitions
            // and
            k1 = 0.05 // also
            k2 = 0.12
            """

        self.model_with_redundant = """
            #! rules
            K(S{u}).B()::cyt => K(S{p})::cyt + B()::cyt + D(A{_})::cell @ 3*[K().B()::cyt]/2*v_1
            K().B()::cyt => K()::cyt + B()::cyt + D(A{_})::cell @ 3*[K().B()::cyt]/2*v_1
            K().K()::cyt => K()::cyt + K()::cyt
            K(S{i}).K()::cyt => K(S{a})::cyt + K()::cyt
            K(S{i}, T{p}).K()::cyt => K(S{a}, T{p})::cyt + K()::cyt

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep

            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """

        self.model_without_redundant = """
            #! rules
            K().B()::cyt => K()::cyt + B()::cyt + D(A{_})::cell @ 3*[K().B()::cyt]/2*v_1
            K().K()::cyt => K()::cyt + K()::cyt

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep

            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """

        self.model_with_context = """
            #! rules
            K(S{i}).B(T{a})::cyt => K(S{i})::cyt + B(T{a})::cyt @ 3*[K(S{i}).B(T{a})::cyt]/2*v_1
            A{p}.K(S{i},T{i})::cyt => A{i}::cyt + K(S{a},T{a})::cyt
            K(S{i},T{i})::cyt => K(S{a},T{i})::cyt

            #! inits
            2 K(S{i}).B(T{a})::cyt
            1 A{p}.K(S{i},T{i})::cyt

            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """

        self.model_without_context = """
            #! rules
            K().B()::cyt => K()::cyt + B()::cyt @ 3*[K().B()::cyt]/2*v_1
            A{_}.K()::cyt => A{_}::cyt + K()::cyt

            #! inits
            2 K().B()::cyt
            1 A{_}.K()::cyt

            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """

        self.model_reachable = """
            #! rules
            K(S{i}).B()::cyt => K(S{a})::cyt + B()::cyt @ 3*[K(S{i}).B()::cyt]/2*v_1
            K(S{a})::cyt + A{i}::cyt => K(S{a}).A{i}::cyt
            K().A{i}::cyt => K().A{a}::cyt

            #! inits
            2 K(S{i}).B()::cyt
            1 A{i}::cyt

            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """

        self.model_nonreachable = """
            #! rules
            K(S{i}).B()::cyt => K(S{a})::cyt + B()::cyt @ 3*[K(S{i}).B()::cyt]/2*v_1
            K(S{a})::cyt + A{i}::cyt => K(S{a}).A{i}::cyt

            #! inits
            2 K(S{i}).B()::cyt
            1 A{i}::cyt

            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """
        
        self.model_parametrised = """
            #! rules
            // commenting
            X(K{i})::rep => X(K{p})::rep @ k1*[X()::rep] // also here
            X(T{a})::rep => X(T{o})::rep @ k2*[Z()::rep]
            => Y(P{f})::rep @ 1/(v_3+([X()::rep])**4) // ** means power (^)

            #! inits
            2 X(K{c}, T{e}).X(K{c}, T{j})::rep
            Y(P{g}, N{l})::rep // comment just 1 item

            #! definitions
            k1 = 0.05
            """

        self.miyoshi = """
            #! rules
            S{u}:KaiC():KaiC6::cyt => S{p}:KaiC():KaiC6::cyt @ (kcat1*[KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            S{p}:KaiC():KaiC6::cyt => S{u}:KaiC():KaiC6::cyt @ (kcat2*[KaiB4{a}.KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            T{u}:KaiC():KaiC6::cyt => T{p}:KaiC():KaiC6::cyt @ (kcat3*[KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            T{p}:KaiC():KaiC6::cyt => T{u}:KaiC():KaiC6::cyt @ (kcat4*[KaiB4{a}.KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            KaiB4{i}::cyt => KaiB4{a}::cyt @ (kcatb2*[KaiB4{i}::cyt])/(Kmb2 + [KaiB4{i}::cyt])
            KaiB4{a}::cyt => KaiB4{i}::cyt @ (kcatb1*[KaiB4{a}::cyt])/(Kmb1 + [KaiB4{a}::cyt])
            KaiB4{a}.KaiA2()::cyt => KaiB4{a}::cyt + KaiA2()::cyt @ k12*[KaiB4{a}.KaiA2()::cyt]
            KaiC6::cyt => 6 KaiC()::cyt @ kdimer*[KaiC6::cyt]
            6 KaiC()::cyt => KaiC6::cyt @ kdimer*[KaiC()::cyt]*([KaiC()::cyt] - 1)*([KaiC()::cyt] - 2)*([KaiC()::cyt] - 3)*([KaiC()::cyt] - 4)*([KaiC()::cyt] - 5)

            #! inits
            6 KaiC(S{p},T{p})::cyt
            1 KaiB4{a}.KaiA2()::cyt

            #! definitions
            kcat1 = 0.539
            kcat3 = 0.89
            Km = 0.602
            kcatb2 = 0.346
            kcatb1 = 0.602
            Kmb2 = 66.75
            Kmb1 = 2.423
            k12 = 0.0008756
            kdimer = 1.77

            #! complexes
            KaiC6 = KaiC().KaiC().KaiC().KaiC().KaiC().KaiC()
            """

        self.miyoshi_non_param = """
            #! rules
            S{u}:KaiC():KaiC6::cyt => S{p}:KaiC():KaiC6::cyt @ (kcat1*[KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            S{p}:KaiC():KaiC6::cyt => S{u}:KaiC():KaiC6::cyt @ (kcat2*[KaiB4{a}.KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            T{u}:KaiC():KaiC6::cyt => T{p}:KaiC():KaiC6::cyt @ (kcat3*[KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            T{p}:KaiC():KaiC6::cyt => T{u}:KaiC():KaiC6::cyt @ (kcat4*[KaiB4{a}.KaiA2()::cyt]*[KaiC6::cyt])/(Km + [KaiC6::cyt])
            KaiB4{i}::cyt => KaiB4{a}::cyt @ (kcatb2*[KaiB4{i}::cyt])/(Kmb2 + [KaiB4{i}::cyt])
            KaiB4{a}::cyt => KaiB4{i}::cyt @ (kcatb1*[KaiB4{a}::cyt])/(Kmb1 + [KaiB4{a}::cyt])
            KaiB4{a}.KaiA2()::cyt => KaiB4{a}::cyt + KaiA2()::cyt @ k12*[KaiB4{a}.KaiA2()::cyt]
            KaiC6::cyt => 6 KaiC()::cyt @ kdimer*[KaiC6::cyt]
            6 KaiC()::cyt => KaiC6::cyt @ kdimer*[KaiC()::cyt]
            KaiC().KaiC()::cyt => KaiC()::cyt + KaiC()::cyt @ kcat1

            #! inits
            6 KaiC(S{p},T{p})::cyt
            1 KaiB4{a}.KaiA2()::cyt
            1 KaiC(S{u},T{p})::cyt
            1 KaiC(S{u},T{p}).KaiC(S{p},T{p})::cyt

            #! definitions
            kcat2 = 0.539
            kcat4 = 0.89
            kcat1 = 0.539
            kcat3 = 0.89
            Km = 0.602
            kcatb2 = 0.346
            kcatb1 = 0.602
            Kmb2 = 66.75
            Kmb1 = 2.423
            k12 = 0.0008756
            kdimer = 1.77

            #! complexes
            KaiC6 = KaiC().KaiC().KaiC().KaiC().KaiC().KaiC()
            """

        self.model_for_matching = """
            #! rules
            K(S{i}).B()::cyt + C{_}::cell => K(S{i})::cyt + B()::cyt + C{_}::cell @ 3*[K(S{i}).B()::cyt]/2*v_1
            A{p}.K(S{i})::cyt => A{i}::cyt + K(S{a})::cyt + C{a}::cyt @ 0.3*[A{p}.K(S{i})::cyt]
            K(S{i},T{i})::cyt + C{_}::cell => K(S{a},T{i})::cyt @ k2*[K(S{i},T{i})::cyt]
            C{_}::cell + C{_}::cell => C{_}.C{_}::cell @ v_1*[C{_}::cell]**2
            C{_}::cell + K()::cell => C{_}.K()::cell @ v_1*[C{_}::cell]**2
    
            #! inits
            2 K(S{i},T{i}).B(T{a})::cyt
            1 A{p}.K(S{i},T{i})::cyt
            2 C{i}::cell
            1 C{a}::cell
    
            #! definitions
            v_1 = 0.05
            k2 = 0.12
            """

    def test_str(self):
        model = self.model_parser.parse(self.model_str_1).data
        back_to_str = repr(model)
        parsed_again = self.model_parser.parse(back_to_str).data
        self.assertEqual(model, parsed_again)

    def test_comments(self):
        model_with_comments = self.model_parser.parse(self.model_with_comments)
        model_without_comments = self.model_parser.parse(self.model_str_2).data

        self.assertEqual(model_with_comments.data, model_without_comments)

    def test_parser(self):
        self.assertEqual(self.model_parser.parse(self.model_str_1).data, self.model)

    def test_signatures(self):
        model = self.model_parser.parse(self.model_str_2).data
        self.assertEqual(model.atomic_signature, {'K': {'c', 'i', 'p'}, 'T': {'e', 'a', 'o', 'j'},
                                                  'P': {'g', 'f'}, 'N': {'l'}})
        self.assertEqual(model.structure_signature, {'X': {'K', 'T'}, 'Y': {'P', 'N'}})

    def test_to_vector_model(self):
        model = self.model_parser.parse(self.model_str_1).data
        self.assertTrue(model.to_vector_model() == self.vm_1)

    def test_parser_errors(self):
        self.assertEqual(self.model_parser.parse(self.model_wrong_1).data,
                         {"unexpected": ";", "expected": {'?', 'name'}, "line": 3, "column": 37})

        self.assertEqual(self.model_parser.parse(self.model_wrong_2).data,
                         {"expected": {'decimal', '#! inits', ']', '#! definitions', '=>', '@', 'int',
                                       '+', 'name', ';'},
                          "line": 3, "column": 26, "unexpected": "="})

    def test_zooming_syntax(self):
        model_abstract = self.model_parser.parse(self.model_with_complexes).data
        model_base = self.model_parser.parse(self.model_without_complexes).data
        self.assertEqual(model_abstract, model_base)

    def test_variables(self):
        model_abstract = self.model_parser.parse(self.model_with_variable).data
        model_base = self.model_parser.parse(self.model_without_variable).data
        self.assertEqual(model_abstract, model_base)

    def test_redundant(self):
        model = self.model_parser.parse(self.model_with_redundant).data
        model.eliminate_redundant()

        model_eliminated = self.model_parser.parse(repr(model)).data
        model_check = self.model_parser.parse(self.model_without_redundant).data
        self.assertEqual(model_eliminated, model_check)

    def test_reduce_context(self):
        model = self.model_parser.parse(self.model_with_context).data
        model.reduce_context()

        model_check = self.model_parser.parse(self.model_without_context).data
        self.assertEqual(model, model_check)

    def test_nonreachability(self):
        complex_parser = Parser("rate_complex")
        agent = "K(S{a}).A{a}::cyt"
        complex = complex_parser.parse(agent).data.children[0]

        model_reach = self.model_parser.parse(self.model_reachable).data
        model_nonreach = self.model_parser.parse(self.model_nonreachable).data

        self.assertTrue(model_reach.static_non_reachability(complex))
        self.assertFalse(model_nonreach.static_non_reachability(complex))

    def test_parametrised_model(self):
        model = self.model_parser.parse(self.model_parametrised).data
        self.assertTrue(len(model.params) == 2)

    def test_create_complex_labels(self):
        model = Model(set(), collections.Counter(), dict(), set())
        complex_parser = Parser("rate_complex")
        complex_1 = complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        complex_2 = complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        complex_3 = complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]
        complex_abstract = complex_parser.parse("K(S{a}).B{_}::cyt").data.children[0]

        ordering = (complex_1, complex_2, complex_3)
        complexes = [complex_2, complex_abstract, complex_1]

        result_labels = {complex_2: "VAR_1",complex_abstract: "ABSTRACT_VAR_12", complex_1: "VAR_0"}
        result_formulas = ['ABSTRACT_VAR_12 = VAR_1+VAR_2; // K(S{a}).B{_}::cyt']

        labels, prism_formulas = model.create_complex_labels(complexes, ordering)
        self.assertEqual(labels, result_labels)
        self.assertEqual(prism_formulas, result_formulas)

    def test_create_AP_labels(self):
        model = Model(set(), collections.Counter(), dict(), set())

        complex_parser = Parser("rate_complex")
        complex_1 = complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        complex_2 = complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        complex_3 = complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]

        complex_abstract = complex_parser.parse("K(S{a}).B{_}::cyt").data.children[0]

        ordering = (complex_1, complex_2, complex_3)

        APs = [Core.Formula.AtomicProposition(complex_abstract, " >= ", "3"),
               Core.Formula.AtomicProposition(complex_1, " < ", 2)]

        s1 = MemorylessState(np.array((1, 2, 2)))
        s2 = MemorylessState(np.array((5, 1, 1)))
        s3 = MemorylessState(np.array((2, 4, 3)))
        s4 = MemorylessState(np.array((1, 4, 3)))

        states_encoding = {s1: 1, s2: 2, s3: 3, s4: 4}

        result_AP_lables = {APs[0]: 'property_0', APs[1]: 'property_1'}
        result_state_labels = {1: {'property_0', 'property_1'},
                               3: {'property_0', 'init'},
                               4: {'property_0', 'property_1'}}

        ts = TS.TransitionSystem.TransitionSystem(ordering)
        ts.states_encoding = states_encoding
        ts.init = 3

        state_labels, AP_lables = model.create_AP_labels(APs, ts, 0)
        self.assertEqual(state_labels, result_state_labels)
        self.assertEqual(AP_lables, result_AP_lables)

    def test_create_unique_agents(self):
        model = self.model_parser.parse(self.miyoshi).data

        reactions = set()
        unique_complexes = set()

        for rule in model.rules:
            reactions |= rule.create_reactions(model.atomic_signature, model.structure_signature)

        for reaction in reactions:
            unique_complexes |= set(reaction.lhs.to_counter()) | set(reaction.rhs.to_counter())

        unique_complexes |= set(model.init)

        ordering = model.create_ordering()
        self.assertEqual(unique_complexes, set(ordering))

    def test_network_free_simulation(self):
        model = self.model_parser.parse(self.miyoshi_non_param).data
        result = model.network_free_simulation(5)
