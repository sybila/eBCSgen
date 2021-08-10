import collections
import multiprocessing
import random
import time
import numpy as np

import pandas as pd
import copy
from sortedcontainers import SortedList

from Core.Atomic import AtomicAgent
from Core.Complex import Complex
from Core.Side import Side
from TS.DirectTS import DirectTS
from TS.State import FullMemoryState, OneStepMemoryState, MultisetState
from TS.TSworker import DirectTSworker
from TS.VectorModel import VectorModel, handle_number_of_threads


class Model:
    def __init__(self, rules: set, init: collections.Counter, definitions: dict, params: set, regulation=None):
        self.rules = rules  # set of Rules
        self.init = init  # Counter: Complex -> int
        self.definitions = definitions  # dict str -> float
        self.params = params  # set of str
        self.all_rates = True  # indicates whether model is quantitative
        self.regulation = regulation  # used to rules filtering, can be unspecified (None)

        # autocomplete
        self.atomic_signature, self.structure_signature = self.extract_signatures()

    def __eq__(self, other: 'Model') -> bool:
        return self.rules == other.rules and self.init == other.init and self.definitions == other.definitions

    def __str__(self):
        return "Model:\n" + "\n".join(map(str, self.rules)) + "\n\n" + str(self.init) + "\n\n" + str(self.definitions) \
               + "\n\n" + str(self.atomic_signature) + "\n" + str(self.structure_signature) + "\n" + str(self.regulation)

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

    def network_free_simulation(self, max_time: float):
        """
        Direct simulation method using Network-free Gillespie method.

        :param max_time: maximal simulation time
        :return: generated dataframe containing simulated time series
        """
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

    def compute_bound(self):
        """
        Estimates bound from the rules and initial state.

        :return: obtained bound
        """
        bound = 0
        for rule in self.rules:
            bound = max(bound, max(rule.lhs.most_frequent(), rule.rhs.most_frequent()))
        return max(bound, Side(self.init).most_frequent())

    def generate_direct_transition_system(self, max_time: float = np.inf, max_size: float = np.inf, bound=None):
        """
        Generates transition system using direct rule firing.

        :param max_time: max time for TS generating before interrupting
        :param max_size: max allowed size of TS before interrupting
        :param bound: bound for individual elements
        :return: generated transitions system
        """
        ts = DirectTS(bound)
        if self.regulation:
            if self.regulation.memory == 0:
                ts.init = MultisetState(self.init)
            elif self.regulation.memory == 1:
                ts.init = OneStepMemoryState(self.init)
            else:
                ts.init = FullMemoryState(self.init)
        else:
            ts.init = MultisetState(self.init)
        ts.unprocessed = {ts.init}
        ts.unique_complexes.update(set(ts.init.multiset))

        for rule in self.rules:
            # precompute complexes for each rule
            rule.lhs, rule.rhs = rule.create_complexes()
            rule.rate_agents, _ = rule.rate.get_params_and_agents()

        if not bound:
            bound = self.compute_bound()
        self.bound = bound

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

        return ts


def update_state(state, consumed, produced):
    consumed = collections.Counter(consumed)
    produced = collections.Counter(produced)
    return state - consumed + produced
