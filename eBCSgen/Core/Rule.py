import collections
import itertools
import random
from copy import copy, deepcopy

from eBCSgen.Core.Rate import Rate
from eBCSgen.Core.Complex import Complex
from eBCSgen.Core.Side import Side
from eBCSgen.Core.Reaction import Reaction
from eBCSgen.TS.State import Multiset


def column(lst, index):
    return tuple(map(lambda x: x[index], lst))


class Rule:
    def __init__(self, agents: tuple, mid: int, compartments: list, complexes: list, pairs: list, rate: Rate, label=None):
        """
        Class to represent BCSL rule

        :param agents: tuple of Atomic/Structure agents in the order as given by the rule
        :param mid: index of first agent from right-hand side
        :param compartments: list assigning to each position a compartment (for each agent)
        :param complexes: list of pairs (from, to) indicating where the complex starts and ends
        :param pairs: entangled agents from LHS to RHS
        :param rate: string representing expression
        """
        self.agents = agents
        self.mid = mid
        self.compartments = compartments
        self.complexes = complexes
        self.pairs = pairs
        self.rate = rate
        self.label = label
        self.comment = (False, [])

    def __eq__(self, other: 'Rule'):
        return self.agents == other.agents and self.mid == other.mid and self.compartments == other.compartments and \
               self.complexes == other.complexes and self.pairs == other.pairs and str(self.rate) == str(other.rate)

    def __repr__(self):
        return str(self)

    def __str__(self):
        lhs, rhs = self.create_complexes()
        rate = " @ " + str(self.rate) if self.rate else ""
        pre_comment, post_comment = "", ""
        if self.comment[1]:
            comment = "// redundant #{" + ", ".join(list(map(str, self.comment[1]))) + "} "
            pre_comment = comment + "// " if self.comment[0] else ""
            post_comment = " " + comment if not self.comment[0] else ""

        label = str(self.label) + " ~ " if self.label else ""

        return label + pre_comment + " + ".join(lhs.to_list_of_strings()) + \
               " => " + " + ".join(rhs.to_list_of_strings()) + rate + post_comment

    def __lt__(self, other):
        return str(self) < str(other)

    def __hash__(self):
        return hash(str(self))

    def get_unique_complexes_from_rule(self) -> dict:
        """
        Creates complexes from rule and returns them in dict.
        Keys are Complex agents, values are sets of all found isomorphisms in SBML code.

        :return: dict of {Complexes:{SBML codes of all isomorphisms in set}}
        """
        unique_complexes_from_rule = dict()
        for (f, t) in self.complexes:
            c = Complex(self.agents[f:t + 1], self.compartments[f])
            double =  (c, c.to_SBML_species_code())
            unique_complexes_from_rule[c] = unique_complexes_from_rule.get(c, set()) | {double}
        return unique_complexes_from_rule

    def create_complexes(self):
        """
        Creates left- and right-hand sides of rule as multisets of Complexes.

        :return: two multisets of Complexes represented as object Side
        """
        lhs, rhs = [], []
        for (f, t) in self.complexes:
            c = Complex(self.agents[f:t + 1], self.compartments[f])
            lhs.append(c) if t < self.mid else rhs.append(c)
        return Side(lhs), Side(rhs)

    def to_reaction(self) -> Reaction:
        """
        Converts Rule to Reactions -> complicated rule structure is simplified to multiset (resp. Side)
        representation of both sides.

        :return: created Reaction
        """
        lhs, rhs = self.create_complexes()
        return Reaction(lhs, rhs, copy(self.rate), self.label)

    def rate_to_vector(self, ordering, definitions: dict):
        """
        Converts all occurrences of Complexes in rate to vector representation.

        :param ordering: given ordering of unique of Complexes (as sortedcontainers.SortedList)
        :param definitions: dict of (param_name, value)
        """
        if self.rate:
            self.rate.vectorize(ordering, definitions)

    def create_reactions(self, atomic_signature: dict, structure_signature: dict) -> set:
        """
        Create all possible reactions.
        Decide if rule is of replication type and call corresponding lower level method.

        :param atomic_signature: given mapping of atomic name to possible states
        :param structure_signature: given mapping of structure name to possible atomics
        :return: set of created reactions
        """
        unique_lhs_indices = set(column(self.pairs, 0))
        if len(self.pairs) > 1 and len(unique_lhs_indices) == 1 and None not in unique_lhs_indices:
            # should be the replication rule
            return self._create_replication_reactions(atomic_signature, structure_signature)
        else:
            return self._create_normal_reactions(atomic_signature, structure_signature)

    def _create_replication_reactions(self, atomic_signature: dict, structure_signature: dict) -> set:
        """
        Create reaction from rule of special form for replication (A -> 2 A)

        :param atomic_signature:  given mapping of atomic name to possible states
        :param structure_signature: given mapping of structure name to possible atomics
        :return: set of created reactions
        """
        # create only for first pair
        l, r = self.pairs[0]
        left = self.agents[l]
        right = self.agents[r]
        results = left.add_context(right, atomic_signature, structure_signature)

        reactions = set()
        for result in results:
            new_agents = list(result)
            # replicate RHS agent n times
            for _ in range(len(self.pairs)):
                new_agents.append(deepcopy(new_agents[-1]))
            new_rule = Rule(tuple(new_agents), self.mid, self.compartments,
                            self.complexes, self.pairs, self.rate, self.label)
            reactions.add(new_rule.to_reaction())

        return reactions

    def _create_normal_reactions(self, atomic_signature: dict, structure_signature: dict) -> set:
        """
        Adds context to all agents and generated all possible combinations.
        Then, new rules with these enhances agents are generated and converted to Reactions.

        :param atomic_signature: given mapping of atomic name to possible states
        :param structure_signature: given mapping of structure name to possible atomics
        :return: set of created reactions
        """
        results = []
        for (l, r) in self.pairs:
            if l is None:
                right = -1
                left = self.agents[r]
            elif r is None:
                right = 1
                left = self.agents[l]
            else:
                left = self.agents[l]
                right = self.agents[r]
            results.append(left.add_context(right, atomic_signature, structure_signature))

        reactions = set()
        for result in itertools.product(*results):
            new_agents = tuple(filter(None, column(result, 0) + column(result, 1)))
            new_rule = Rule(new_agents, self.mid, self.compartments, self.complexes, self.pairs, self.rate, self.label)
            reactions.add(new_rule.to_reaction())

        return reactions

    def compatible(self, other: 'Rule') -> bool:
        """
        Checks whether Rule is compatible (position-wise) with the other Rule.
        Is done by formaly translating to Reactions (just a better object handling).

        :param other: given Rule
        :return: True if compatible
        """
        self_reaction = self.to_reaction()
        other_reaction = other.to_reaction()
        return self_reaction.compatible(other_reaction)

    def reduce_context(self):
        """
        Reduces context of Rule to minimum.
        Includes both agents and Rate.

        :return: new Rule with reduced context
        """
        new_agents = tuple([agent.reduce_context() for agent in self.agents])
        new_rate = self.rate.reduce_context() if self.rate else None
        return Rule(new_agents, self.mid, self.compartments, self.complexes, self.pairs, new_rate)

    def is_meaningful(self) -> bool:
        """
        Checks whether the Rule does any change, i.e. is meaningful.
        Done by translating to Reaction and comparing its sides.

        :return: True if meaningful
        """
        reaction = self.to_reaction()
        return not reaction.lhs == reaction.rhs

    def exists_compatible_agent(self, agent: Complex) -> bool:
        """
        Checks whether there exists a compatible agent in the rhs of the rule.

        :param agent: given Complex agent
        :return: True if exists compatible
        """
        reaction = self.to_reaction()
        return reaction.rhs.exists_compatible_agent(agent)

    def create_all_compatible(self, atomic_signature: dict, structure_signature: dict):
        """
        Creates all fully specified complexes for all both Sides

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: set of all created Complexes
        """
        return self.to_reaction().create_all_compatible(atomic_signature, structure_signature)

    def evaluate_rate(self, state, params):
        """
        Evaluate rate based on current state and parameter values.

        :param state: given state
        :param params: mapping of params to its value
        :return: a real number of the rate
        """
        values = dict()
        for (state_complex, count) in state.content.value.items():
            for agent in self.rate_agents:
                if agent.compatible(state_complex):
                    values[agent] = values.get(agent, 0) + count
        return self.rate.evaluate_direct(values, params)

    def match(self, state, all=False):
        """
        Find all possible matches of the rule to given state.

        :param state: given state
        :param all: bool to indicate if choose one matching randomly or return all of them
        :return: random match/all matches
        """
        state = deepcopy(state.content.value)
        matches = find_all_matches(self.lhs.agents, state)
        matches = [sum(match, []) for match in matches]

        if len(matches) == 0:
            return None
        if not all:
            return random.choice(matches)
        return matches

    def replace(self, aligned_match):
        """
        Apply rule to chosen match.
        Match contains agents which satisfy LHS of the rule an can be safely replaced based on RHS

        :param aligned_match: complexes fitting LHS of the rule
        :return: multiset replaced according to the match
        """
        # replace respective agents

        unique_lhs_indices = set(column(self.pairs, 0))
        if len(self.pairs) > 1 and len(unique_lhs_indices) == 1 and \
                None not in unique_lhs_indices and len(aligned_match) == 1:
            resulting_rhs = self._replace_replicated_rhs(aligned_match[0])
        else:
            resulting_rhs = self._replace_normal_rhs(aligned_match)

        # construct resulting complexes
        output_complexes = []
        for (f, t) in list(filter(lambda item: item[0] >= self.mid, self.complexes)):
            output_complexes.append(Complex(resulting_rhs[f - self.mid:t - self.mid + 1], self.compartments[f]))

        return Multiset(collections.Counter(output_complexes))

    def _replace_normal_rhs(self, aligned_match):
        """
        Replace in normal mode.

        :param aligned_match: complexes fitting LHS of the rule
        :return: RHS with replaced agents
        """
        resulting_rhs = []
        for i, rhs_agent in enumerate(self.agents[self.mid:]):
            if len(aligned_match) <= i:
                resulting_rhs.append(rhs_agent)
            else:
                resulting_rhs.append(rhs_agent.replace(aligned_match[i]))
        return resulting_rhs

    def _replace_replicated_rhs(self, aligned_agent):
        """
        Replace in replication mode (special form for replication A -> 2 A)

        :param aligned_agent: complex fitting LHS of the rule
        :return: RHS with replaced agents
        """
        resulting_rhs = []

        rhs_agent = self.agents[self.mid]
        rhs_agent = rhs_agent.replace(aligned_agent)

        for _ in range(len(self.pairs)):
            resulting_rhs.append(deepcopy(rhs_agent))
        return resulting_rhs

    def reconstruct_complexes_from_match(self, match):
        """
        Create complexes from agents matched to the LHS

        :param match: value of
        :return: multiset of constructed agents
        """
        output_complexes = []
        for (f, t) in list(filter(lambda item: item[1] < self.mid, self.complexes)):
            output_complexes.append(Complex(match[f:t + 1], self.compartments[f]))
        return Multiset(collections.Counter(output_complexes))

    def create_reversible(self):
        """
        Create a reversible version of the rule with _bw label.

        Also add implicit _fw label to current Rule.

        TODO: allow two rates

        :return: reversed Rule
        """
        agents = self.agents[self.mid:] + self.agents[:self.mid]
        mid = len(self.agents) - self.mid
        compartments = self.compartments[self.mid:] + self.compartments[:self.mid]
        complexes = sorted([((f - self.mid) % len(self.agents),
                             (t - self.mid) % len(self.agents)) for (f, t) in self.complexes])
        pairs = []
        for (l, r) in self.pairs:
            if l is None or r is None:
                pairs.append((r, l))
            else:
                pairs.append((l, r))

        rate = self.rate
        label = None
        if self.label:
            label = self.label + "_bw"
            self.label += "_fw"

        return Rule(agents, mid, compartments, complexes, pairs, rate, label)


def find_all_matches(lhs_agents, state):
    """
    Finds all possible matches which actually can be used for given state.

    :param lhs_agents: given LHS of a rule
    :param state: state to be applied to
    :return: candidates for match
    """
    choices = []
    if len(lhs_agents) == 0:
        return [choices]

    lhs_complex = lhs_agents[0]
    for candidate in list(state):
        if lhs_complex.compatible(candidate):
            state[candidate] -= 1
            aligns = candidate.align_match(lhs_complex)
            for branch in find_all_matches(lhs_agents[1:], deepcopy(+state)):
                for align in aligns:
                    choices.append([align] + branch)
    return choices
