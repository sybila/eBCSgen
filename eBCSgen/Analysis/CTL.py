from pyModelChecking.CTL.model_checking import modelcheck
from pyModelChecking.CTL.parser import Parser

from eBCSgen.Core.Formula import Formula
from eBCSgen.TS.TransitionSystem import TransitionSystem


class CTL:
    @staticmethod
    def model_checking(ts: TransitionSystem, CTL_formula: Formula):
        APs = CTL_formula.get_APs()

        state_labels, AP_labels = ts.create_AP_labels(APs, include_init=False)
        formula = CTL_formula.replace_APs(AP_labels, extra_quotes=False)

        kripke = ts.to_kripke(state_labels)
        parser = Parser()
        formula = parser(str(formula))
        result = modelcheck(kripke, formula)
        return ts.init in result, result
