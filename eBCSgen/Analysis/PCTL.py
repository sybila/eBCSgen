import subprocess

from eBCSgen.TS.TransitionSystem import TransitionSystem
from eBCSgen.Core.Formula import Formula
from eBCSgen.Errors.StormNotAvailable import StormNotAvailable


class PCTL:
    @staticmethod
    def model_checking(ts: TransitionSystem, PCTL_formula: Formula):
        """
        Model checking of given PCTL formula.

        First, Storm explicit file is generated from given transition system and
        appropriate PCTL formula issues are resolved (e.g. naming of agents). Finally,
        Storm model checker is called and results are returned.

        :param ts: given transition system
        :param PCTL_formula: given PCTL formula
        :return: output of Storm model checker
        """
        path = "/tmp/"
        # generate labels and give them to save_storm
        APs = PCTL_formula.get_APs()
        state_labels, AP_labels = ts.create_AP_labels(APs)
        formula = PCTL_formula.replace_APs(AP_labels)
        transitions_file = path + "exp_transitions.tra"
        labels_file = path + "exp_labels.lab"
        ts.save_to_STORM_explicit(transitions_file, labels_file, state_labels, AP_labels)

        command = "storm --explicit {0} {1} --prop '{2}'"
        result = call_storm(command.format(transitions_file, labels_file, formula))
        return result

    @staticmethod
    def parameter_synthesis(ts: TransitionSystem, PCTL_formula: Formula, region: str):
        """
        Parameter synthesis of given PCTL formula in given region.

        First, Storm explicit file is generated from given transition system
        and appropriate PCTL formula issues are resolved (e.g. naming of agents).
        Finally, Storm model checker is called and results are returned.

        :param ts: given transition system
        :param PCTL_formula: given PCTL formula
        :param region: string representation of region which will be checked by Storm
        :return: output of Storm model checker
        """
        path = "/tmp/"

        labels, prism_formulas = PCTL_formula.create_complex_labels(ts.ordering)
        formula = PCTL_formula.replace_complexes(labels)

        prism_file = path + "prism-parametric.pm"

        ts.save_to_prism(prism_file, ts.params, prism_formulas)

        command_region = "storm-pars --prism {0} --prop '{1}' --region '{2}' --refine 0.01 10 --printfullresult"
        command_no_region = "storm-pars --prism {0} --prop '{1}'"

        if region:
            result = call_storm(command_region.format(prism_file, formula, region))
        else:
            result = call_storm(command_no_region.format(prism_file, formula))
        return result


def call_storm(command: str):
    """
    Calls Storm model checker locally.

    :param command: given command to be executed
    :return: result of Storm execution
    """
    status, result = subprocess.getstatusoutput('storm')
    if status == 0:
        command = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = command.communicate()
        return stdout
    else:
        raise StormNotAvailable
