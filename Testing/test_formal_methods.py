import subprocess
import unittest

from sympy.printing.tests.test_numpy import np

from Core.Model import Model
from Core.Complex import Complex
from Core.Structure import StructureAgent
from TS.Edge import Edge
from TS.State import State
from TS.TransitionSystem import TransitionSystem


class TestFormalMethods(unittest.TestCase):
    def setUp(self):
        """
        Model 1
        Analysis of a PRISM model of the Knuth-Yao die
        storm website
        """
        self.str1 = StructureAgent("S", set())
        self.str2 = StructureAgent("D", set())

        self.c1 = Complex([self.str1], "rep")
        self.c2 = Complex([self.str2], "rep")

        ordering = (self.c1, self.c2)

        self.s1 = State(np.array((0, 0)))
        self.s2 = State(np.array((1, 0)))
        self.s3 = State(np.array((2, 0)))
        self.s4 = State(np.array((3, 0)))
        self.s5 = State(np.array((4, 0)))
        self.s6 = State(np.array((5, 0)))
        self.s7 = State(np.array((6, 0)))
        self.s8 = State(np.array((7, 1)))
        self.s9 = State(np.array((7, 2)))
        self.s10 = State(np.array((7, 3)))
        self.s11 = State(np.array((7, 4)))
        self.s12 = State(np.array((7, 5)))
        self.s13 = State(np.array((7, 6)))

        self.die_ts = self.ts_eq_1 = TransitionSystem(ordering)
        self.ts_eq_1.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2, self.s4: 3, self.s5: 4,
                                        self.s6: 5, self.s7: 6, self.s8: 7, self.s9: 8, self.s10: 9,
                                        self.s11: 10, self.s12: 11, self.s13: 12}
        self.die_ts.edges = {Edge(0, 1, 0.5), Edge(0, 2, 0.5), Edge(1, 2, 0.5), Edge(1, 3, 0.5), Edge(2, 4, 0.5),
                             Edge(2, 5, 0.5), Edge(3, 1, 0.5), Edge(3, 7, 0.5), Edge(4, 8, 0.5), Edge(4, 9, 0.5),
                             Edge(5, 10, 0.5), Edge(5, 11, 0.5), Edge(6, 2, 0.5), Edge(6, 12, 0.5), Edge(7, 7, 1),
                             Edge(8, 8, 1), Edge(9, 9, 1), Edge(10, 10, 1), Edge(11, 11, 1), Edge(12, 12, 1)}

        # TODO -> model definition
        # self.defs = {}
        # self.inits = collections.Counter({self.c1: 0, self.c2: 0})
        # self.die_model = self.model = Model({}, self.inits, self.defs, None)

        self.die_prism = """
dtmc

module die

    // local state
    s : [0..7] init 0;
    // value of the dice
    d : [0..6] init 0;
    
    [] s=0 -> 0.5 : (s'=1) + 0.5 : (s'=2);
    [] s=1 -> 0.5 : (s'=3) + 0.5 : (s'=4);
    [] s=2 -> 0.5 : (s'=5) + 0.5 : (s'=6);
    [] s=3 -> 0.5 : (s'=1) + 0.5 : (s'=7) & (d'=1);
    [] s=4 -> 0.5 : (s'=7) & (d'=2) + 0.5 : (s'=7) & (d'=3);
    [] s=5 -> 0.5 : (s'=7) & (d'=4) + 0.5 : (s'=7) & (d'=5);
    [] s=6 -> 0.5 : (s'=2) + 0.5 : (s'=7) & (d'=6);
    [] s=7 -> (s'=7);

endmodule

rewards "coin_flips"
    [] s<7 : 1;
endrewards
        """
        self.die_pctl1 = "P=? [F \"one\"]"
        self.die_pctl2 = "P=? [F s=7&d=1]"
        self.die_transitions = """dtmc
0 1 0.5
0 2 0.5
1 3 0.5
1 4 0.5
2 5 0.5
2 6 0.5
3 1 0.5
3 7 0.5
4 8 0.5
4 9 0.5
5 10 0.5
5 11 0.5
6 2 0.5
6 12 0.5
7 7 1
8 8 1
9 9 1
10 10 1
11 11 1
12 12 1
        """

    # TODO missing test for label file, ordering of target state does not correspond
    def test_explicit_file(self):
        self.die_ts.save_to_STORM_explicit("explicit_transitions.tra", "explicit_labels.lab")
        # self.assertEqual(open("explicit_transitions.tra", "r").read(), self.die_transitions)

    # TODO bcsl model for die example labeling file
    def test_model_checking(self):
        # model_checking1 = self.die_model.PCTL_model_checking(self.die_pctl1)
        out = subprocess.Popen(
            ['storm', '--explicit', 'die.tra', 'die.lab', '--prop', self.die_pctl1],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        # self.assertEqual(model_checking1, stdout)

    # TODO
    def test_prism_file(self):
        # bound does not correspond to model 1
        self.die_ts.init = 6
        self.die_ts.save_to_prism("prism_dtmc.pm", 7, {"p", "q"}, ['ABSTRACT_VAR_12 = VAR_1+VAR_2',
                                                                   'ABSTRACT_VAR_34 = VAR_3+VAR_4'])
        print(open("prism_dtmc.pm", "r").read())
        # self.assertEqual(open("prism_dtmc.pm", "r").read(), self.die_prism)

    # TODO
    def test_parameter_synthesis(self):
        self.assertEqual("", "")
