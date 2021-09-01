from pyModelChecking.CTL.model_checking import modelcheck
from pyModelChecking.CTL.parser import Parser

from Core.Formula import Formula
from TS.TransitionSystem import TransitionSystem


class CTL:
    @staticmethod
    def model_checking(ts: TransitionSystem, CTL_formula: Formula):
        APs = CTL_formula.get_APs()

        state_labels, AP_labels = ts.create_AP_labels(APs, include_init=False)
        formula = CTL_formula.replace_APs(AP_labels, extra_quotes=False)

        print(AP_labels)

        for key, value in state_labels.items():
            print(key, value)

        kripke = ts.to_kripke(state_labels)
        parser = Parser()
        formula = parser(str(formula))
        result = modelcheck(kripke, formula)
        return ts.init in result, result
