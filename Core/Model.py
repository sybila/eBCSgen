import collections

from Core.Side import Side
from TS.TransitionSystem import TransitionSystem
from TS.VectorModel import VectorModel
from Parsing.ParsePCTLformula import PCTLparser
import subprocess


class Model:
    def __init__(self, rules: set, init: collections.Counter, definitions: dict, params: set):
        self.rules = rules
        self.init = init
        self.definitions = definitions
        self.params = params
        self.all_rates = True

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
        for rule in self.rules:
            if rule.rate is None:
                self.all_rates = False
            for agent in rule.agents:
                atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
        for agent in list(self.init):
            atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
        return atomic_signature, structure_signature

    def to_vector_model(self, bound: int = None) -> VectorModel:
        """
        Creates vector representation of the model.

        First reactions are generated, then unique complexes are collected and finally both reactions and
        initial state are transformed to vector representation.

        THIS SHOULD BE DONE IN PARALLEL !!!

        :param bound: given bound
        :return: VectorModel representation of the model
        """
        reactions = set()
        unique_complexes = set()
        for rule in self.rules:
            reactions |= rule.create_reactions(self.atomic_signature, self.structure_signature)

        for reaction in reactions:
            unique_complexes |= set(reaction.lhs.to_counter()) | set(reaction.rhs.to_counter())
        unique_complexes |= set(self.init)
        ordering = tuple(sorted(unique_complexes))

        init = Side(self.init.elements()).to_vector(ordering)
        vector_reactions = set()
        for reaction in reactions:
            vector_reactions.add(reaction.to_vector(ordering, self.definitions))

        return VectorModel(vector_reactions, init, ordering, bound)

    def eliminate_redundant(self):
        pass

    def network_free_simulation(self, options) -> list:
        # for this we need to be able to apply Rule on State
        pass

    def PCTL_model_checking(self, PCTL_formula: str, bound: int = None):
        """
        Model checking of given PCTL formula.

        First transition system is generated, then Storm explicit file is generated and
        appropriate PCTL formula issues resolved are (e.g. naming of agents). Finally,
        Storm model checker is called and results are returned.

        :param PCTL_formula: given PCTL formula
        :param bound: given bound
        :return: output of Storm model checker
        """
        path = "Testing/"
        vm = self.to_vector_model(bound)
        ts = vm.generate_transition_system()
        formula = PCTLparser().parse(PCTL_formula)
        if not formula.success:
            return formula.data

        # generate labels and give them to save_storm
        APs = formula.get_APs()
        state_labels, AP_labeles = self.create_AP_labels(APs, ts, vm.bound)
        formula = formula.replace_APs(AP_labeles)
        ts.save_to_STORM_explicit(path + "exp_transitions.tra", path + "exp_labels.lab", state_labels, AP_labeles)

        command = "storm --explicit {0} {1} --prop '{2}'"
        command = subprocess.Popen(command.format(path + 'exp_transitions.tra', path + 'exp_labels.lab', formula),
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        stdout, stderr = command.communicate()
        return stdout

    def PCTL_synthesis(self, PCTL_formula: str, region: str, bound: int = None):
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
        :return: output of Storm model checker
        """
        path = "/tmp/"
        vm = self.to_vector_model(bound)
        ts = vm.generate_transition_system()
        formula = PCTLparser().parse(PCTL_formula)
        if not formula.success:
            return formula.data

        labels, prism_formulas = self.create_complex_labels(formula.get_complexes(), ts.ordering)
        formula = formula.replace_complexes(labels)

        ts.save_to_prism(path + "prism-parametric.pm", vm.bound, self.params, prism_formulas)

        command_region = "storm-pars --prism {0} --prop '{1}' --region '{2}' --refine 0.01 10 --printfullresult"
        command_no_region = "storm-pars --prism {0} --prop '{1}'"

        if region:
            command = subprocess.Popen(command_region.format(path + 'prism-parametric.pm', formula, region),
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        else:
            command = subprocess.Popen(command_no_region.format(path + 'prism-parametric.pm', formula),
                                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        stdout, stderr = command.communicate()
        return stdout

    # def save_to_STORM_explicit(self, transitions_file: str, labels_file: str, labels: dict):
    #     ts = self.to_vector_model().generate_transition_system()
    #     ts.save_to_STORM_explicit(transitions_file, labels_file, labels)
    #
    # def save_to_prism(self, output_file: str, prism_formulas: list):
    #     ts = self.to_vector_model().generate_transition_system()
    #     ts.save_to_prism(output_file, self.bound, self.params, prism_formulas)

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
