from pyModelChecking.CTL.model_checking import modelcheck

from Core.Formula import Formula
from TS.TransitionSystem import TransitionSystem


class CTL:
    @staticmethod
    def model_checking(ts: TransitionSystem, CTL_formula: Formula):
        APs = CTL_formula.get_APs()
        state_labels, AP_labels = ts.create_AP_labels(APs)
        formula = CTL_formula.replace_APs(AP_labels)

        kripke = ts.to_kripke(state_labels)
        result = modelcheck(kripke, formula)
        print(result)
