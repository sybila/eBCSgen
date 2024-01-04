import unittest
import re

from sympy.printing.tests.test_numpy import np

from eBCSgen.TS.Edge import Edge
from eBCSgen.TS.TransitionSystem import TransitionSystem

import Testing.objects_testing as objects


def get_storm_result(cmd: str):
    result = cmd.split("Result")
    if len(result) < 2:
        return "ERROR"
    else:
        return re.search(r"\d+\.\d+", result[1]).group()


path = "Testing/test_die/"


class TestFormalMethods(unittest.TestCase):
    def setUp(self):

        """
        Model 1 - Transition system of die model
        Analysis of a PRISM example model from the Knuth-Yao
        source: storm website
        """
        ordering = (objects.c21, objects.c22)

        self.die_ts = TransitionSystem(ordering, 6)
        self.die_ts.init = 0
        self.die_ts.states_encoding = {0: objects.state3, 1: objects.state4, 2: objects.state5, 3: objects.state6, 4: objects.state7,
                                       5: objects.state8, 6: objects.state9, 7: objects.state10, 8: objects.state11, 9: objects.state12,
                                       10: objects.state13, 11: objects.state14, 12: objects.state15}
        self.die_ts.edges = {Edge(0, 1, 0.5), Edge(0, 2, 0.5), Edge(1, 3, 0.5), Edge(1, 4, 0.5), Edge(2, 5, 0.5),
                             Edge(2, 6, 0.5), Edge(3, 1, 0.5), Edge(3, 7, 0.5), Edge(4, 8, 0.5), Edge(4, 9, 0.5),
                             Edge(5, 10, 0.5), Edge(5, 11, 0.5), Edge(6, 2, 0.5), Edge(6, 12, 0.5), Edge(7, 7, 1),
                             Edge(8, 8, 1), Edge(9, 9, 1), Edge(10, 10, 1), Edge(11, 11, 1), Edge(12, 12, 1)}

        # die parametric TS
        self.die_ts_parametric = TransitionSystem(ordering, 6)
        self.die_ts_parametric.init = 0
        self.die_ts_parametric.states_encoding = {0: objects.state3, 1: objects.state4, 2: objects.state5, 3: objects.state6, 4: objects.state7,
                                                  5: objects.state8, 6: objects.state9, 7: objects.state10, 8: objects.state11, 9: objects.state12,
                                                  10: objects.state13, 11: objects.state14, 12: objects.state15}
        self.die_ts_parametric.edges = {Edge(0, 1, "p"), Edge(0, 2, "(1-p)"), Edge(1, 3, "p"), Edge(1, 4, "(1-p)"),
                                        Edge(2, 5, "p"),
                                        Edge(2, 6, "(1-p)"), Edge(3, 1, "p"), Edge(3, 7, "(1-p)"), Edge(4, 8, "p"),
                                        Edge(4, 9, "(1-p)"),
                                        Edge(5, 10, "p"), Edge(5, 11, "(1-p)"), Edge(6, 2, "p"), Edge(6, 12, "(1-p)"),
                                        Edge(7, 7, 1),
                                        Edge(8, 8, 1), Edge(9, 9, 1), Edge(10, 10, 1), Edge(11, 11, 1), Edge(12, 12, 1)}

        self.labels = {0: {'init'}, 7: {'one', 'done'},
                       9: {'done'}, 8: {'done'}, 10: {'done'}, 11: {'done'}, 12: {'done'}}

        # PCTL formulas for model checking
        self.die_pctl_prism = "P=? [F VAR_0=7&VAR_1=1]"  # 0.1666666667
        self.die_pctl_explicit = "P=? [F \"one\"]"  # 0.1666666667
        self.die_pctl_parametric = "P=? [F VAR_0=7&VAR_1=1]"
        self.die_pctl1 = "P=? [F VAR_0=7&VAR_1=1 || F VAR_0=7&VAR_1<4]"  # 0.3333333333 not used
        self.die_pctl2 = "P<=0.15 [F VAR_0=7&VAR_1=1]"  # false not used
        self.result = 0.166666667

    # Test explicit files (die model). Checking equality with example files
    def test_die_explicit_tra(self):
        self.die_ts.save_to_STORM_explicit(path + "die_explicit.tra", path + "die_explicit.lab",
                                           self.labels, {0: "one", 1: "done"})
        with open(path + "die_explicit.tra", "r") as our_file:
            with open(path + "die.tra", "r") as test_file:
                self.assertEqual(our_file.read(), test_file.read())

    def test_die_explicit_lab(self):
        self.die_ts.save_to_STORM_explicit(path + "die_explicit.tra", path + "die_explicit.lab",
                                           self.labels, {0: "one", 1: "done"})
        # test keywords
        with open(path + "die_explicit.lab", "r") as file:
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
        test_ass = {0: {"init"}, 7: {'one', 'done'},
                    9: {'done'}, 8: {'done'}, 10: {'done'}, 11: {'done'}, 12: {'done'}}
        self.assertEqual(our_labels, test_ass)

    # Test non-parametric prism file (die model). Checking equality with example file modified die.pm from storm web.
    def test_die_pm(self):
        self.die_ts.save_to_prism(path + "die_prism.pm", set(), [])
        with open(path + "die.pm") as f:
            test_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        with open(path + "die_prism.pm") as f:
            our_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        self.assertEqual(test_prism, our_prism)

    def test_prism_parametric(self):
        self.die_ts_parametric.save_to_prism(path + "die_prism_parametric.pm", {"p"}, [])
        with open(path + "parametric_die.pm") as f:
            test_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        with open(path + "die_prism_parametric.pm") as f:
            our_prism = re.sub(r"\s+", "", f.read(), flags=re.UNICODE)
        self.assertEqual(test_prism, our_prism)
