import subprocess

from TS.TransitionSystem import TransitionSystem
from Core import Formula
from Errors.StormNotAvailable import StormNotAvailable


class PCTL:
    @staticmethod
    def model_checking(ts: TransitionSystem, PCTL_formula: Formula, storm_local: bool = True):
        """
        Model checking of given PCTL formula.

        First transition system is generated, then Storm explicit file is generated and
        appropriate PCTL formula issues resolved are (e.g. naming of agents). Finally,
        Storm model checker is called and results are returned.

        :param ts: given transition system
        :param PCTL_formula: given PCTL formula
        :param storm_local: use local Storm installation
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
        result = call_storm(command.format(transitions_file, labels_file, formula),
                            [transitions_file, labels_file], storm_local)
        return result

    @staticmethod
    def parameter_synthesis(ts: TransitionSystem, PCTL_formula: Formula, region: str, storm_local: bool = True):
        """
        Parameter synthesis of given PCTL formula in given region.

        First transition system is generated, PRISM file with encoded explicit TS is generated
        and appropriate PCTL formula issues are resolved (e.g. naming of agents). Finally,
        Storm model checker is called and results are returned.

        :param ts: given transition system
        :param PCTL_formula: given PCTL formula
        :param region: string representation of region which will be checked by Storm
        :param storm_local: use local Storm installation
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
            result = call_storm(command_region.format(prism_file, formula, region), [prism_file], storm_local)
        else:
            result = call_storm(command_no_region.format(prism_file, formula), [prism_file], storm_local)
        return result


def call_storm(command: str, files: list, storm_local: bool):
    """
    Calls Storm model checker either locally or on the remote server.

    :param command: given command to be executed
    :param files: files to be transferred to remote device
    :param storm_local: use local Storm installation
    :return: result of Storm execution
    """
    if storm_local:
        return call_local_storm(command)
    else:
        import paramiko, scp
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        try:
            ssh.connect("psyche07.fi.muni.cz", username="biodivine")
        except Exception:
            return call_local_storm(command)

        with scp.SCPClient(ssh.get_transport()) as tunnel:
            for file in files:
                tunnel.put(file, file)

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        output = ssh_stdout.read()
        stderr = ssh_stderr.read()
        ssh.close()
        del ssh, ssh_stdin, ssh_stdout, ssh_stderr

        # if error output is empty, command was executed successfully, call local Storm otherwise
        if stderr:
            return call_local_storm(command)
        else:
            return output


def call_local_storm(command: str):
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
