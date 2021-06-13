import collections
import multiprocessing
import random
import subprocess
import time
import numpy as np

import pandas as pd
import copy
from sortedcontainers import SortedList

from Core.Formula import Formula
from Core.Atomic import AtomicAgent
from Core.Complex import Complex
from Core.Side import Side
from TS.DirectTS import DirectTS
from TS.State import FullMemoryState, OneStepMemoryState, MultisetState
from TS.TSworker import DirectTSworker
from TS.TransitionSystem import TransitionSystem
from TS.VectorModel import VectorModel, handle_number_of_threads
from Errors.ComplexOutOfScope import ComplexOutOfScope
from Errors.StormNotAvailable import StormNotAvailable


class Model:
    def __init__(self, rules: set, init: collections.Counter, definitions: dict, params: set):
        self.rules = rules  # set of Rules
        self.init = init  # Counter: Complex -> int
        self.definitions = definitions  # dict str -> float
        self.params = params  # set of str
        self.all_rates = True  # indicates whether model is quantitative
        self.regulation = None  # used to rules filtering, can be unspecified

        # autocomplete
        self.atomic_signature, self.structure_signature = self.extract_signatures()

    def __eq__(self, other: 'Model') -> bool:
        return self.rules == other.rules and self.init == other.init and self.definitions == other.definitions

    def __str__(self):
        return "Model:\n" + "\n".join(map(str, self.rules)) + "\n\n" + str(self.init) + "\n\n" + str(self.definitions) \
               + "\n\n" + str(self.atomic_signature) + "\n" + str(self.structure_signature)

    def __repr__(self):
        return "#! rules\n" + "\n".join(map(str, self.rules)) + \
               "\n\n#! inits\n" + "\n".join([str(self.init[a]) + " " + str(a) for a in self.init]) + \
               "\n\n#! definitions\n" + "\n".join([str(p) + " = " + str(self.definitions[p]) for p in self.definitions])

    def extract_signatures(self):
        """
        Automatically creates signature from context of rules and initial state.
        Additionally it checks if all rules have a rate, sets all_rates to False otherwise.

        :return: created atomic and structure signatures
        """
        atomic_signature, structure_signature = dict(), dict()
        atomic_names = set()
        for rule in self.rules:
            if rule.rate is None:
                self.all_rates = False
            for agent in rule.agents:
                atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
                if type(agent) == AtomicAgent:
                    atomic_names.add(agent.name)
        for agent in list(self.init):
            atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
            atomic_names |= agent.get_atomic_names()
        for name in atomic_names:
            if name not in atomic_signature:
                atomic_signature[name] = {"_"}
        return atomic_signature, structure_signature

    def create_ordering(self) -> SortedList:
        """
        Extracts all possible unique agents from the model and gives them fixed order using SortedList.

        :return: SortedList of unique agents
        """
        unique_complexes = set()
        for rule in self.rules:
            unique_complexes |= rule.create_all_compatible(self.atomic_signature, self.structure_signature)

        unique_complexes |= set(self.init)
        return SortedList(unique_complexes)

    def to_vector_model(self, bound: int = None) -> VectorModel:
        """
        Creates vector representation of the model.

        First reactions are generated, then unique complexes are collected and finally both reactions and
        initial state are transformed to vector representation.

        :param bound: given bound
        :return: VectorModel representation of the model
        """
        ordering = self.create_ordering()
        reactions = set()

        for rule in self.rules:
            rule_copy = copy.deepcopy(rule)
            rule_copy.rate_to_vector(ordering, self.definitions)
            reactions |= rule_copy.create_reactions(self.atomic_signature, self.structure_signature)

        init = Side(self.init.elements()).to_vector(ordering)
        vector_reactions = set()

        for reaction in reactions:
            vector_reactions.add(reaction.to_vector(ordering, self.definitions))

        return VectorModel(vector_reactions, init, ordering, bound)

    def eliminate_redundant(self):
        """
        Adds comments to rules which are potentially redundant.

        In the case when there are no rule present, it automatically comments out the redundant rules.
        """
        counter = 1
        for rule_left in self.rules:
            for rule_right in self.rules:
                if id(rule_left) != id(rule_right):
                    if rule_left.compatible(rule_right):
                        rule_right.comment = (not self.all_rates, rule_right.comment[1] + [counter])
                        rule_left.comment[1].append(counter)
                        counter += 1

    def reduce_context(self):
        """
        Reduces context of the Model to the minimum.
        Includes all rules and initial state.
        """
        new_rules = set()
        for rule in self.rules:
            new_rule = rule.reduce_context()
            if new_rule.is_meaningful():
                new_rules.add(new_rule)

        new_init = collections.Counter()
        for init in self.init:
            new_init[init.reduce_context()] = self.init[init]

        self.init = new_init
        self.rules = new_rules

    def static_non_reachability(self, agent: Complex) -> bool:
        """
        Checks whether there exists a rule with compatible agent in its rhs.

        :param agent: given Complex agent
        :return: True if exists compatible
        """
        return any(list(map(lambda a: a.exists_compatible_agent(agent), self.rules)))

    def PCTL_model_checking(self, PCTL_formula: Formula, bound: int = None, storm_local: bool = True):
        """
        Model checking of given PCTL formula.

        First transition system is generated, then Storm explicit file is generated and
        appropriate PCTL formula issues resolved are (e.g. naming of agents). Finally,
        Storm model checker is called and results are returned.

        :param PCTL_formula: given PCTL formula
        :param bound: given bound
        :param storm_local: use local Storm installation
        :return: output of Storm model checker
        """
        path = "/tmp/"
        vm = self.to_vector_model(bound)
        ts = vm.generate_transition_system()

        # generate labels and give them to save_storm
        APs = PCTL_formula.get_APs()
        state_labels, AP_labeles = self.create_AP_labels(APs, ts, vm.bound)
        formula = PCTL_formula.replace_APs(AP_labeles)
        transitions_file = path + "exp_transitions.tra"
        labels_file = path + "exp_labels.lab"
        ts.save_to_STORM_explicit(transitions_file, labels_file, state_labels, AP_labeles)

        command = "storm --explicit {0} {1} --prop '{2}'"
        result = call_storm(command.format(transitions_file, labels_file, formula),
                            [transitions_file, labels_file], storm_local)
        return result

    def PCTL_synthesis(self, PCTL_formula: Formula, region: str, bound: int = None, storm_local: bool = True):
        """
        Parameter synthesis of given PCTL formula in given region.

        First transition system is generated, PRISM file with encoded explicit TS is generated
        and appropriate PCTL formula issues are resolved (e.g. naming of agents). Finally,
        Storm model checker is called and results are returned.

        Note: rates of the model could be checked on "linearity", then PRISM file could be maybe computed
            directly with no need of TS generating.

        :param PCTL_formula: given PCTL formula
        :param region: string representation of region which will be checked by Storm
        :param bound: given bound
        :param storm_local: use local Storm installation
        :return: output of Storm model checker
        """
        path = "/tmp/"
        vm = self.to_vector_model(bound)
        ts = vm.generate_transition_system()

        labels, prism_formulas = self.create_complex_labels(PCTL_formula.get_complexes(), ts.ordering)
        formula = PCTL_formula.replace_complexes(labels)

        prism_file = path + "prism-parametric.pm"

        ts.save_to_prism(prism_file, vm.bound, self.params, prism_formulas)

        command_region = "storm-pars --prism {0} --prop '{1}' --region '{2}' --refine 0.01 10 --printfullresult"
        command_no_region = "storm-pars --prism {0} --prop '{1}'"

        if region:
            result = call_storm(command_region.format(prism_file, formula, region), [prism_file], storm_local)
        else:
            result = call_storm(command_no_region.format(prism_file, formula), [prism_file], storm_local)
        return result

    def create_complex_labels(self, complexes: list, ordering: tuple):
        """
        Creates label for each unique Complex from Formula.
        This covers two cases - ground and abstract Complexes.
        For the abstract ones, a PRISM formula needs to be constructed as a sum
            of all compatible complexes.

        :param complexes: list of extracted complexes from Formula
        :param ordering: given complex ordering of TS
        :return: unique label for each Complex and list of PRISM formulas for abstract Complexes
        """
        labels = dict()
        prism_formulas = list()
        for complex in complexes:
            if complex in ordering:
                labels[complex] = complex.to_PRISM_code(ordering.index(complex))
            else:
                indices = complex.identify_compatible(ordering)
                if not indices:
                    raise ComplexOutOfScope(complex)
                id = "ABSTRACT_VAR_" + "".join(list(map(str, indices)))
                labels[complex] = id
                prism_formulas.append(id + " = " + "+".join(["VAR_{}".format(i) for i in indices]) +
                                      "; // " + str(complex))
        return labels, prism_formulas

    def create_AP_labels(self, APs: list, ts: TransitionSystem, bound: int):
        """
        Creates label for each AtomicProposition.
        Moreover, goes through all states in ts.states_encoding and validates whether they satisfy give
         APs - if so, the particular label is assigned to the state.

        :param APs: give AtomicProposition extracted from Formula
        :param ts: given TS
        :param bound: given bound
        :return: dictionary of State_code -> set of labels and AP -> label
        """
        AP_lables = dict()
        for ap in APs:
            AP_lables[ap] = "property_" + str(len(AP_lables))

        state_labels = dict()
        ts.change_hell(bound)
        for state in ts.states_encoding.keys():
            for ap in APs:
                if state.check_AP(ap, ts.ordering):
                    state_labels[ts.states_encoding[state]] = \
                        state_labels.get(ts.states_encoding[state], set()) | {AP_lables[ap]}
        state_labels[ts.init] = state_labels.get(ts.init, set()) | {"init"}
        return state_labels, AP_lables

    def network_free_simulation(self, max_time: float):
        state = FullMemoryState(copy.deepcopy(self.init))
        for rule in self.rules:
            # precompute complexes for each rule
            rule.lhs, _ = rule.create_complexes()
            rule.rate_agents, _ = rule.rate.get_params_and_agents()

        history = dict()
        collected_agents = set(state.multiset)
        time = 0.0
        history[time] = state.multiset
        used_rules = []
        while time < max_time:
            candidate_rules = pd.DataFrame(data=[(rule,
                                                  rule.evaluate_rate(state, self.definitions),
                                                  rule.match(state)) for rule in self.rules],
                                           columns=["rule", "rate", "match"])

            # drop rules which cannot be actually used (do not pass stoichiometry check)
            candidate_rules = candidate_rules.dropna()

            if self.regulation:
                rules = {item: None for item in candidate_rules['rule']}
                state.used_rules = used_rules
                applicable_rules = self.regulation.filter(state, rules)
                candidate_rules = candidate_rules[candidate_rules['rule'].isin(applicable_rules)]

            if not candidate_rules.empty:
                rates_sum = candidate_rules['rate'].sum()
                sorted_candidates = candidate_rules.sort_values(by=["rate"])
                sorted_candidates["cumsum"] = sorted_candidates["rate"].cumsum()

                # pick random rule based on rates
                rand_number = rates_sum * random.random()
                sorted_candidates.drop(sorted_candidates[sorted_candidates["cumsum"] < rand_number].index, inplace=True)

                # apply chosen rule to matched agents
                match = sorted_candidates.iloc[0]["match"]
                rule = sorted_candidates.iloc[0]["rule"]
                produced_agents = rule.replace(match)

                # update state based on match & replace operation
                match = rule.reconstruct_complexes_from_match(match)
                state = FullMemoryState(update_state(state.multiset, match, produced_agents))
                if self.regulation:
                    used_rules.append(rule.label)
            else:
                rates_sum = random.uniform(0.5, 0.9)

            # update time
            time += random.expovariate(rates_sum)
            collected_agents = collected_agents.union(set(state.multiset))
            history[time] = state.multiset

        # create pandas DataFrame
        ordered_agents = list(collected_agents)
        header = list(map(str, ordered_agents))
        df = pd.DataFrame(columns=header)
        for time in history:
            vector = [history[time][agent] for agent in ordered_agents]
            df.loc[time] = vector

        df.index.name = 'times'
        df.reset_index(inplace=True)
        return df

    def generate_direct_transition_system(self, ts=None, max_time: float = np.inf, max_size: float = np.inf):
        if not ts:
            ts = DirectTS()
            if self.regulation.memory == 0:
                init = MultisetState(self.init)
            elif self.regulation.memory == 1:
                init = OneStepMemoryState(self.init)
            else:
                init = FullMemoryState(self.init)
            ts.unprocessed = {init}
            ts.unique_complexes.update(set(init.multiset))
        else:
            pass
            # TODO: if a TS is given, extract all the data

        for rule in self.rules:
            # precompute complexes for each rule
            rule.lhs, _ = rule.create_complexes()
            rule.rate_agents, _ = rule.rate.get_params_and_agents()

        workers = [DirectTSworker(ts, self) for _ in range(multiprocessing.cpu_count())]
        for worker in workers:
            worker.start()

        workers[0].work.set()
        start_time = time.time()

        try:
            while any([worker.work.is_set() for worker in workers]) \
                    and time.time() - start_time < max_time \
                    and len(ts.processed) < max_size:
                handle_number_of_threads(len(ts.unprocessed), workers)
                time.sleep(1)
        except (KeyboardInterrupt, EOFError) as e:
            pass

        for worker in workers:
            worker.join()

        while any([worker.is_alive() for worker in workers]):
            time.sleep(1)

        # transform to classic TS (vectors)
        normal_ts = ts.to_TS(init)
        return normal_ts


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


def update_state(state, consumed, produced):
    consumed = collections.Counter(consumed)
    produced = collections.Counter(produced)
    return state - consumed + produced
