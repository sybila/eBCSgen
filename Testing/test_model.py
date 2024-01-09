import unittest
import collections
from unittest import mock
from lark import Tree

import numpy as np

from eBCSgen.Core.Formula import Formula
from eBCSgen.Core.Model import Model
from eBCSgen.Core.Rate import Rate
from eBCSgen.TS.State import Vector, State, Memory
from eBCSgen.TS.VectorModel import VectorModel
from eBCSgen.TS.VectorReaction import VectorReaction
from eBCSgen.Core.Formula import AtomicProposition
from eBCSgen.TS.TransitionSystem import TransitionSystem

from Testing.models.get_model_str import get_model_str
import Testing.objects_testing as objects


class TestModel(unittest.TestCase):
    def setUp(self):
        # inits
        self.inits = collections.Counter({objects.c27: 2, objects.c28: 1})

        # defs
        self.defs = {'k1': 0.05, 'k2': 0.12}

        self.model = Model({objects.r1, objects.r2, objects.r3}, self.inits, self.defs, set())
        # model

        self.model_str_1 = get_model_str("model1")

        self.model_str_2 = get_model_str("model2")

        # vectors

        ordering = (objects.c27, objects.c28, objects.c29)

        rate_expr = "1/(1+([X()::rep])**4)"
        rate_1 = Rate(objects.rate_parser.parse(rate_expr).data)
        rate_1.vectorize(ordering, dict())

        rate_expr = "k1*[X()::rep]"
        rate_2 = Rate(objects.rate_parser.parse(rate_expr).data)
        rate_2.vectorize(ordering, {"k1": 0.05})

        rate_3 = Rate(Tree('rate', [Tree('fun', [1.0])]))

        init = State(Vector(np.array([2, 1, 0])), Memory(0))

        vector_reactions = {VectorReaction(State(Vector(np.array([0, 0, 0])), Memory(0)),
                                           State(Vector(np.array([0, 1, 0])), Memory(0)),
                                           rate_1),
                            VectorReaction(State(Vector(np.array([1, 0, 0])), Memory(0)),
                                           State(Vector(np.array([0, 0, 0])), Memory(0)),
                                           rate_2),
                            VectorReaction(State(Vector(np.array([0, 0, 1])), Memory(0)),
                                           State(Vector(np.array([1, 0, 0])), Memory(0)),
                                           rate_3)}

        self.vm_1 = VectorModel(vector_reactions, init, ordering, None)
        
        self.model_with_complexes = get_model_str("model_with_complexes")

        self.model_without_complexes = get_model_str("model_without_complexes")

        self.model_with_variable = get_model_str("model_with_variable")

        self.model_without_variable = get_model_str("model_without_variable")

        self.model_with_redundant = get_model_str("model_with_redundant")

        self.model_without_redundant = get_model_str("model_without_redundant")

        self.model_with_context = get_model_str("model_with_context")

        self.model_without_context = get_model_str("model_without_context")

        self.model_reachable = get_model_str("model_reachable")

        self.model_nonreachable = get_model_str("model_nonreachable")
        
        self.model_parametrised = get_model_str("model_parametrised")

        self.miyoshi = get_model_str("model_miyoshi")

        self.miyoshi_non_param = get_model_str("model_miyoshi_non_param")

        self.model_for_matching = get_model_str("model_for_matching")

        self.model_for_bound = get_model_str("model_for_bound")

    def test_str(self):
        model = objects.model_parser.parse(self.model_str_1).data
        back_to_str = repr(model)
        parsed_again = objects.model_parser.parse(back_to_str).data
        self.assertEqual(model, parsed_again)

    def test_signatures(self):
        model = objects.model_parser.parse(self.model_str_2).data
        self.assertEqual(model.atomic_signature, {'K': {'c', 'i', 'p'}, 'T': {'e', 'a', 'o', 'j'},
                                                  'P': {'g', 'f'}, 'N': {'l'}})
        self.assertEqual(model.structure_signature, {'X': {'K', 'T'}, 'Y': {'P', 'N'}})

    def test_to_vector_model(self):
        model = objects.model_parser.parse(self.model_str_1).data
        self.assertTrue(model.to_vector_model() == self.vm_1)

    def test_zooming_syntax(self):
        model_abstract = objects.model_parser.parse(self.model_with_complexes).data
        model_base = objects.model_parser.parse(self.model_without_complexes).data
        self.assertEqual(model_abstract, model_base)

    def test_variables(self):
        model_abstract = objects.model_parser.parse(self.model_with_variable).data
        model_base = objects.model_parser.parse(self.model_without_variable).data
        self.assertEqual(model_abstract, model_base)

    def test_redundant(self):
        model = objects.model_parser.parse(self.model_with_redundant).data
        model.eliminate_redundant()

        model_eliminated = objects.model_parser.parse(repr(model)).data
        model_check = objects.model_parser.parse(self.model_without_redundant).data
        self.assertEqual(model_eliminated, model_check)

    def test_reduce_context(self):
        model = objects.model_parser.parse(self.model_with_context).data
        model.reduce_context()

        model_check = objects.model_parser.parse(self.model_without_context).data
        self.assertEqual(model, model_check)

    def test_nonreachability(self):
        agent = "K(S{a}).A{a}::cyt"
        complex = objects.rate_complex_parser.parse(agent).data.children[0]

        model_reach = objects.model_parser.parse(self.model_reachable).data
        model_nonreach = objects.model_parser.parse(self.model_nonreachable).data

        self.assertTrue(model_reach.static_non_reachability(complex))
        self.assertFalse(model_nonreach.static_non_reachability(complex))

    def test_parametrised_model(self):
        model = objects.model_parser.parse(self.model_parametrised).data
        self.assertTrue(len(model.params) == 2)

    def test_create_complex_labels(self):
        complex_1 = objects.rate_complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        complex_2 = objects.rate_complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        complex_3 = objects.rate_complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]
        complex_abstract = objects.rate_complex_parser.parse("K(S{a}).B{_}::cyt").data.children[0]

        ordering = (complex_1, complex_2, complex_3)
        complexes = [complex_2, complex_abstract, complex_1]

        result_labels = {complex_2: "VAR_1", complex_abstract: "ABSTRACT_VAR_12", complex_1: "VAR_0"}
        result_formulas = ['ABSTRACT_VAR_12 = VAR_1+VAR_2; // K(S{a}).B{_}::cyt']

        formula = Formula(None, None)
        formula.get_complexes = mock.Mock(return_value=complexes)

        labels, prism_formulas = formula.create_complex_labels(ordering)
        self.assertEqual(labels, result_labels)
        self.assertEqual(prism_formulas, result_formulas)

    def test_create_AP_labels(self):
        complex_1 = objects.rate_complex_parser.parse("K(S{i},T{a}).B{o}::cyt").data.children[0]
        complex_2 = objects.rate_complex_parser.parse("K(S{a},T{a}).B{o}::cyt").data.children[0]
        complex_3 = objects.rate_complex_parser.parse("K(S{a},T{i}).B{o}::cyt").data.children[0]

        complex_abstract = objects.rate_complex_parser.parse("K(S{a}).B{_}::cyt").data.children[0]

        ordering = (complex_1, complex_2, complex_3)

        APs = [AtomicProposition(complex_abstract, " >= ", "3"), AtomicProposition(complex_1, " < ", 2)]

        s1 = State(Vector(np.array((1, 2, 2))), Memory(0))
        s2 = State(Vector(np.array((5, 1, 1))), Memory(0))
        s3 = State(Vector(np.array((2, 4, 3))), Memory(0))
        s4 = State(Vector(np.array((1, 4, 3))), Memory(0))

        states_encoding = {1: s1, 2: s2, 3: s3, 4: s4}

        result_AP_lables = {APs[0]: 'property_0', APs[1]: 'property_1'}
        result_state_labels = {1: {'property_0', 'property_1'},
                               3: {'property_0', 'init'},
                               4: {'property_0', 'property_1'}}

        ts = TransitionSystem(ordering, 5)
        ts.states_encoding = states_encoding
        ts.init = 3

        state_labels, AP_lables = ts.create_AP_labels(APs)
        self.assertEqual(state_labels, result_state_labels)
        self.assertEqual(AP_lables, result_AP_lables)

    def test_create_unique_agents(self):
        model = objects.model_parser.parse(self.miyoshi).data

        reactions = set()
        unique_complexes = set()

        for rule in model.rules:
            reactions |= rule.create_reactions(model.atomic_signature, model.structure_signature)

        for reaction in reactions:
            unique_complexes |= set(reaction.lhs.to_counter()) | set(reaction.rhs.to_counter())

        unique_complexes |= set(model.init)

        ordering = model.create_ordering()
        self.assertEqual(unique_complexes, set(ordering))

    def test_compute_bound(self):
        model = objects.model_parser.parse(self.model_for_bound).data
        for rule in model.rules:
            rule.lhs, rule.rhs = rule.create_complexes()

        self.assertEqual(model.compute_bound(), 2)

    def test_direct_ts_bound(self):
        model = objects.model_parser.parse(self.model_for_bound).data
        rules = set()
        for i, rule in enumerate(model.rules):
            rule.label = 'r{}'.format(i)
            rules.add(rule)
        model.rules = rules
        ts = model.generate_direct_transition_system()
        self.assertEqual(ts.bound, 2)
