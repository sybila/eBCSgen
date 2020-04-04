import subprocess
import unittest

from sympy.printing.tests.test_numpy import np

from TS.Edge import Edge
from TS.TransitionSystem import TransitionSystem
from Core.Structure import StructureAgent
from Core.Complex import Complex
from Parsing.ParseBCSL import Parser
from TS.State import State
import re


class TestFormalMethods(unittest.TestCase):
    def setUp(self):
        self.model_parser = Parser("model")

        """
        Model 1 - Transition system of die model
        Analysis of a PRISM example model from the Knuth-Yao
        source: storm website
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

        self.die_ts = TransitionSystem(ordering)
        self.die_ts.init = 0
        self.die_ts.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2, self.s4: 3, self.s5: 4,
                                       self.s6: 5, self.s7: 6, self.s8: 7, self.s9: 8, self.s10: 9,
                                       self.s11: 10, self.s12: 11, self.s13: 12}
        self.die_ts.edges = {Edge(0, 1, 0.5), Edge(0, 2, 0.5), Edge(1, 3, 0.5), Edge(1, 4, 0.5), Edge(2, 5, 0.5),
                             Edge(2, 6, 0.5), Edge(3, 1, 0.5), Edge(3, 7, 0.5), Edge(4, 8, 0.5), Edge(4, 9, 0.5),
                             Edge(5, 10, 0.5), Edge(5, 11, 0.5), Edge(6, 2, 0.5), Edge(6, 12, 0.5), Edge(7, 7, 1),
                             Edge(8, 8, 1), Edge(9, 9, 1), Edge(10, 10, 1), Edge(11, 11, 1), Edge(12, 12, 1)}

        # die parametric TS
        self.die_ts_parametric = TransitionSystem(ordering)
        self.die_ts_parametric.init = 0
        self.die_ts_parametric.states_encoding = {self.s1: 0, self.s2: 1, self.s3: 2, self.s4: 3, self.s5: 4,
                                       self.s6: 5, self.s7: 6, self.s8: 7, self.s9: 8, self.s10: 9,
                                       self.s11: 10, self.s12: 11, self.s13: 12}
        self.die_ts_parametric.edges = {Edge(0, 1, "p"), Edge(0, 2, "(1-p)"), Edge(1, 3, "p"), Edge(1, 4, "(1-p)"), Edge(2, 5, "p"),
                             Edge(2, 6, "(1-p)"), Edge(3, 1, "p"), Edge(3, 7, "(1-p)"), Edge(4, 8, "p"), Edge(4, 9, "(1-p)"),
                             Edge(5, 10, "p"), Edge(5, 11, "(1-p)"), Edge(6, 2, "p"), Edge(6, 12, "(1-p)"), Edge(7, 7, 1),
                             Edge(8, 8, 1), Edge(9, 9, 1), Edge(10, 10, 1), Edge(11, 11, 1), Edge(12, 12, 1)}

        self.labels = {0: {'init'}, 7: {'one', 'done'},
                       9: {'done'}, 8: {'done'}, 10: {'done'}, 11: {'done'}, 12: {'done'}}

        # PCTL formulas for model checking
        self.die_pctl_prism = "P=? [F VAR_0=7&VAR_1=1]"  # 0.1666666667
        self.die_pctl_explicit = "P=? [F \"one\"]"  # 0.1666666667
        self.die_pctl_parametric = "P=? [F VAR_0=7&VAR_1=1]"
        self.die_pctl1 = "P=? [F VAR_0=7&VAR_1=1 || F VAR_0=7&VAR_1<4]"  # 0.3333333333 not used
        self.die_pctl2 = "P<=0.15 [F VAR_0=7&VAR_1=1]"  # false not used
        self.result = 0.1666666667

    # Test explicit files (die model). Checking equality with example files
    def test_die_explicit_tra(self):
        self.die_ts.save_to_STORM_explicit("test_die/die_explicit.tra", "test_die/die_explicit.lab", self.labels)
        with open("test_die/die_explicit.tra", "r") as our_file:
            with open("test_die/die.tra", "r") as test_file:
                self.assertEqual(our_file.read(), test_file.read())

    # join with previous test?
    # not sure if I can test content of the exact lines (a.k.a our_lab[0].replace("\s", "").startswith("#"))
    def test_die_explicit_lab(self):
        # self.die_ts.save_to_STORM_explicit("die_explicit.tra", "die_explicit.lab", self.labels)
        # test keywords
        with open("test_die/die_explicit.lab", "r") as file:
            our_lab = file.read().split("#DECLARATION")
            if len(our_lab) != 2:
                self.fail("#DECLARATION key is missing")
            our_lab = our_lab[1].split("#END")
            if len(our_lab) != 2:
                self.fail("#END key is missing")

        # test declaration part
        self.assertSetEqual(set(our_lab[0].split()), {"init", "one", "done"})

        # test assignment part
        our_labels = dict()
        assignment = set(our_lab[1].splitlines())
        assignment.remove("")
        for item in assignment:
            our_labels.update({int(item.split()[0]): set(item.replace(item.split()[0], "").split())})
        # print(our_labels)
        test_ass = {0: {"init"}, 7: {'one', 'done'},
                    9: {'done'}, 8: {'done'}, 10: {'done'}, 11: {'done'}, 12: {'done'}}
        self.assertEqual(our_labels, test_ass)

    # Test non-parametric prism file (die model). Checking equality with example file modified die.pm from storm web.
    def test_die_pm(self):
        self.die_ts.save_to_prism("test_die/die_prism.pm", 6, set(), [])
        with open("test_die/die.pm") as f:
            test_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        with open("test_die/die_prism.pm") as f:
            our_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        self.assertEqual(test_prism, our_prism)

    # test model checking with prism and explicit files
    def test_prism_modelchecking(self):
        prism_out = subprocess.Popen(
            ['storm', '--prism', 'test_die/die_prism.pm', '--prop', self.die_pctl_prism],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = prism_out.communicate()
        result = self.get_storm_result(str(stdout))
        if result == "ERROR":
            self.fail(stdout)
        else:
            self.assertEqual(result, str(self.result), "Prism model checking .... done")

    def test_explicit_modelchecking(self):
        explicit_out = subprocess.Popen(
            ['storm', '--explicit', 'test_die/die_explicit.tra', 'test_die/die_explicit.lab', '--prop',
             self.die_pctl_explicit],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = explicit_out.communicate()
        result = self.get_storm_result(str(stdout))
        if result == "ERROR":
            self.fail(stdout)
        else:
            self.assertEqual(result, str(self.result), "Explicit model checking .... done")

    # test parametric prism file
    def test_prism_parametric(self):
        self.die_ts_parametric.save_to_prism("test_die/die_prism_parametric.pm", 6, {"p"}, [])
        with open("test_die/parametric_die.pm") as f:
            test_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        with open("test_die/die_prism_parametric.pm") as f:
            our_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        self.assertEqual(test_prism, our_prism)

    # TODO Mato storm-pars call is not working
    """    # test result from parameter synthesis
    def test_parameter_synthesis(self):
        out = subprocess.Popen(
            ['storm-pars', '--prism', 'test_die/die_prism_parametric.pm', '--prop', self.die_pctl_parametric],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        if "ERROR" in str(stdout):
            self.fail(stdout)
        else:
            result = str(stdout).split("Result (initial states): ")
            result = result[1].split("Time for model checking: ")
            self.assertEqual(result[0], "((p)^2)/(p+1)", "Parameter synthesis .... done")"""

    def get_storm_result(self, cmd: str):
        result = cmd.split("Result")
        if len(result) < 2:
            return "ERROR"
        else:
            return re.search(r"\d+\.\d+", result[1]).group()
