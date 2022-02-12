import unittest
import numpy as np
import sympy

from eBCSgen.Core.Atomic import AtomicAgent
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Structure import StructureAgent
from eBCSgen.Parsing.ParseBCSL import Parser
from eBCSgen.TS.State import Vector, State, Memory
from eBCSgen.Core.Rate import Rate


CORRECT_MATHML = """
<kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML"><apply><divide><times><cn>3.0</cn>\
<ci>K(T{i}).X()::cyt</ci></times><plus><power><ci>K()::cyt</ci><cn>2.0</cn></power><times>\
<cn>4.0</cn><ci>p</ci></times></plus></divide></apply></math></kineticLaw>"""


class TestRate(unittest.TestCase):
    def setUp(self):
        # agents

        self.a1 = AtomicAgent("T", "i")
        self.a2 = AtomicAgent("S", "i")
        self.a3 = AtomicAgent("T", "a")
        self.a4 = AtomicAgent("S", "a")

        self.s1 = StructureAgent("X", {self.a4})
        self.s2 = StructureAgent("X", {self.a2})
        self.s3 = StructureAgent("K", {self.a3})
        self.s4 = StructureAgent("K", {self.a1})
        self.s5 = StructureAgent("X", set())
        self.s6 = StructureAgent("K", set())

        self.c1 = Complex([self.s6], "cyt")  # K()::cyt
        self.c2 = Complex([self.s3], "cyt")  # K(T{a})::cyt
        self.c3 = Complex([self.s4], "cyt")  # K(T{i})::cyt
        self.c4 = Complex([self.s4, self.s1], "cyt")  # K(T{i}).X(S{a})::cyt
        self.c5 = Complex([self.s4, self.s2], "cyt")  # K(T{i}).X(S{i})::cyt
        self.c6 = Complex([self.s3, self.s1], "cyt")  # K(T{a}).X(S{a})::cyt
        self.c7 = Complex([self.s3, self.s2], "cyt")  # K(T{a}).X(S{i})::cyt

        # rates

        self.parser = Parser("rate")
        rate_expr = "3.0*[K()::cyt]/2.0*v_1"

        self.rate_1 = Rate(self.parser.parse(rate_expr).data)

        rate_expr = "3.0*[K(T{i}).X()::cyt] + [K()::cyt]"

        self.rate_2 = Rate(self.parser.parse(rate_expr).data)

        rate_expr = "(3.0*[K()::cyt])/(2.0*v_1)"

        self.rate_3 = Rate(self.parser.parse(rate_expr).data)

        # states

        self.state_1 = State(Vector(np.array([2, 3])), Memory(0))
        self.state_2 = State(Vector(np.array([2, 0, 3, 1, 6, 2])), Memory(0))

    def test_to_str(self):
        self.assertEqual(str(self.rate_1), "3.0*[K()::cyt]/2.0*v_1")

    def test_eq(self):
        self.assertEqual(self.rate_2, self.rate_2)
        self.assertNotEqual(self.rate_1, self.rate_2)

    def test_vectorize(self):
        ordering = (self.c2, self.c3)
        self.assertEqual(self.rate_1.vectorize(ordering, dict()), [Vector(np.array([1, 1]))])
        ordering = (self.c2, self.c3, self.c4, self.c5, self.c6, self.c7)
        self.assertEqual(self.rate_2.vectorize(ordering, dict()),
                         [Vector(np.array([0, 0, 1, 1, 0, 0])), Vector(np.array([1, 1, 0, 0, 0, 0]))])

    def test_evaluate(self):
        ordering = (self.c2, self.c3)
        self.rate_1.vectorize(ordering, {"v_1": 5})
        self.assertEqual(self.rate_1.evaluate(self.state_1), sympy.sympify("3*5.0/2*5"))

        ordering = (self.c2, self.c3, self.c4, self.c5, self.c6, self.c7)
        self.rate_2.vectorize(ordering, dict())
        self.assertEqual(self.rate_2.evaluate(self.state_2), sympy.sympify("3*4.0 + 2"))

    def test_to_symbolic(self):
        ordering = (self.c2, self.c3)
        self.rate_1.vectorize(ordering, dict())
        self.rate_1.to_symbolic()
        self.assertEqual(str(self.rate_1), "3.0*(y[0] + y[1])/2.0*v_1")

        ordering = (self.c2, self.c3, self.c4, self.c5, self.c6, self.c7)
        self.rate_2.vectorize(ordering, dict())
        self.rate_2.to_symbolic()
        self.assertEqual(str(self.rate_2), "3.0*(y[2] + y[3])+(y[0] + y[1])")

    def test_reduce_context(self):
        rate_expr = "3.0*[K(S{i})::cyt]/2.0*v_1"
        rate = Rate(self.parser.parse(rate_expr).data)

        self.assertEqual(rate.reduce_context(), self.rate_1)

    def test_evaluate_direct(self):
        values = {self.c1: 3}
        params = {"v_1": 5}
        self.assertEqual(self.rate_3.evaluate_direct(values, params), 9/10)

    def test_mathML(self):
        rate_expr = "(3.0*[K(T{i}).X()::cyt])/([K()::cyt]**2.0+4.0*p)"
        rate = Rate(self.parser.parse(rate_expr).data)
        expression = rate.to_mathML()
        agents, params = rate.get_params_and_agents()
        str_to_code = {"[" + str(agent) + "]": agent.to_SBML_species_code() for agent in agents}

        operators = {'**': ' ^ ', '*': ' * ', '+': ' + ', '-': ' - ', '/': ' / '}
        for agent in str_to_code:
            rate_expr = rate_expr.replace(agent, str_to_code[agent])
        for op in operators:
            rate_expr = rate_expr.replace(op, operators[op])

        self.assertEqual(expression, rate_expr)
 