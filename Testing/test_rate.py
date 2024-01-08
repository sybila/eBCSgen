import unittest
import numpy as np
import sympy

from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Parsing.ParseBCSL import Parser
from eBCSgen.TS.State import Vector, State, Memory
from eBCSgen.Core.Rate import Rate

import Testing.objects_testing as objects


CORRECT_MATHML = """
<kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML"><apply><divide><times><cn>3.0</cn>\
<ci>K(T{i}).X()::cyt</ci></times><plus><power><ci>K()::cyt</ci><cn>2.0</cn></power><times>\
<cn>4.0</cn><ci>p</ci></times></plus></divide></apply></math></kineticLaw>"""


class TestRate(unittest.TestCase):
    def setUp(self):
        # rates

        self.parser = Parser("rate")
        rate_expr = "3.0*[K()::cyt]/2.0*v_1"

        self.rate_1 = Rate(objects.rate_parser.parse(rate_expr).data)

        rate_expr = "3.0*[K(T{i}).X()::cyt] + [K()::cyt]"

        self.rate_2 = Rate(objects.rate_parser.parse(rate_expr).data)

        rate_expr = "(3.0*[K()::cyt])/(2.0*v_1)"

        self.rate_3 = Rate(objects.rate_parser.parse(rate_expr).data)

    def test_to_str(self):
        self.assertEqual(str(self.rate_1), "3.0*[K()::cyt]/2.0*v_1")

    def test_eq(self):
        self.assertEqual(self.rate_2, self.rate_2)
        self.assertNotEqual(self.rate_1, self.rate_2)

    def test_vectorize(self):
        ordering = (objects.c15, objects.c16)
        self.assertEqual(self.rate_1.vectorize(ordering, dict()), [Vector(np.array([1, 1]))])
        ordering = (objects.c15, objects.c16, objects.c17, objects.c18, objects.c19, objects.c20)
        self.assertEqual(self.rate_2.vectorize(ordering, dict()),
                         [Vector(np.array([0, 0, 1, 1, 0, 0])), Vector(np.array([1, 1, 0, 0, 0, 0]))])

    def test_evaluate(self):
        ordering = (objects.c15, objects.c16)
        self.rate_1.vectorize(ordering, {"v_1": 5})
        self.assertEqual(self.rate_1.evaluate(objects.state1), sympy.sympify("3*5.0/2*5"))

        ordering = (objects.c15, objects.c16, objects.c17, objects.c18, objects.c19, objects.c20)
        self.rate_2.vectorize(ordering, dict())
        self.assertEqual(self.rate_2.evaluate(objects.state2), sympy.sympify("3*4.0 + 2"))

    def test_to_symbolic(self):
        ordering = (objects.c15, objects.c16)
        self.rate_1.vectorize(ordering, dict())
        self.rate_1.to_symbolic()
        self.assertEqual(str(self.rate_1), "3.0*(y[0] + y[1])/2.0*v_1")

        ordering = (objects.c15, objects.c16, objects.c17, objects.c18, objects.c19, objects.c20)
        self.rate_2.vectorize(ordering, dict())
        self.rate_2.to_symbolic()
        self.assertEqual(str(self.rate_2), "3.0*(y[2] + y[3])+(y[0] + y[1])")

    def test_reduce_context(self):
        rate_expr = "3.0*[K(S{i})::cyt]/2.0*v_1"
        rate = Rate(objects.rate_parser.parse(rate_expr).data)

        self.assertEqual(rate.reduce_context(), self.rate_1)

    def test_evaluate_direct(self):
        values = {objects.c14: 3}
        params = {"v_1": 5}
        self.assertEqual(self.rate_3.evaluate_direct(values, params), 9/10)

    def test_mathML(self):
        rate_expr = "(3.0*[K(T{i}).X()::cyt])/([K()::cyt]**2.0+4.0*p)"
        rate = Rate(objects.rate_parser.parse(rate_expr).data)
        expression = rate.to_mathML()
        agents, params = rate.get_params_and_agents()
        str_to_code = {"[" + str(agent) + "]": agent.to_SBML_species_code() for agent in agents}

        operators = {'**': ' ^ ', '*': ' * ', '+': ' + ', '-': ' - ', '/': ' / '}
        for agent in str_to_code:
            rate_expr = rate_expr.replace(agent, str_to_code[agent])
        for op in operators:
            rate_expr = rate_expr.replace(op, operators[op])

        self.assertEqual(expression, rate_expr)
 