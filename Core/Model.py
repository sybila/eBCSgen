import collections

from Core.Complex import Complex
from Core.Side import Side
from TS.State import State
from TS.VectorModel import VectorModel


class Model:
    def __init__(self, rules: set, init: collections.Counter, definitions: dict, bound: int):
        self.rules = rules
        self.init = init
        self.definitions = definitions
        self.bound = bound
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

    def to_vector_model(self) -> VectorModel:
        """
        Creates vector representation of the model.

        First reactions are generated, then unique complexes are collected and finally both reactions and
        initial state are transformed to vector representation.

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

        return VectorModel(vector_reactions, init, ordering, self.bound)

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

    def network_free_simulation(self, options) -> list:
        # for this we need to be able to apply Rule on State
        pass

    def PCTL_model_checking(self, PCTL_formula) -> bool:
        # check whether rate are "linear" -> create directly PRISM file
        # otherwise generate TS and use its explicit representation for Storm
        pass

    def PCTL_synthesis(self, PCTL_formula) -> bool:
        # check whether rate are "linear" -> create directly PRISM file
        # otherwise generate TS and use its explicit representation for Storm
        pass
