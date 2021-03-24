import collections
import itertools

import Core.Atomic


class Complex:
    def __init__(self, agents: list, compartment: str):
        self.agents = agents
        self.compartment = compartment

    def __repr__(self):
        return ".".join(sorted(list(map(str, self.agents)))) + "::" + self.compartment

    def __str__(self):
        return ".".join(list(map(str, self.agents))) + "::" + self.compartment

    def __lt__(self, other: 'Complex'):
        return repr(self) < repr(other)

    def __eq__(self, other: 'Complex'):
        return self.compartment == other.compartment and\
               collections.Counter(self.agents) == collections.Counter(other.agents)

    def __hash__(self):
        return hash((frozenset(collections.Counter(self.agents).items()), self.compartment))

    def get_atomic_names(self) -> set:
        """
        Creates set of all atomic names used in the complex.

        :return: set of all atomic names
        """
        return {agent.name for agent in list(filter(lambda agent: type(agent) == Core.Atomic.AtomicAgent, self.agents))}

    def to_PRISM_code(self, number: int) -> str:
        """
        Creates state variable name for PRISM model.

        :param number: position in ordering
        :return: PRISM variable name
        """
        return "VAR_" + str(number)

    def get_agent_names(self):
        """
        Maps names to all agents in complex
        :return: list of agent names in this complex
        """
        return [agent.name for agent in self.agents]

    def to_SBML_speciesTypes_code(self):
        """
        :return: <str> id of SBML - speciesType of this complex agent

        """
        return "st_"+"_".join(sorted(self.get_agent_names()))

    def to_SBML_species_code(self):
        """Using hash for now. Instead of '-' symbol we use '_'
        so it is compatible with SBML - id naming later some nicer
        id could be implemented

        :return: <str> id of SBML - species of this complex agent"""
        code = str(self.__hash__())
        return "sp_" + code[1:] if code[0] == "-" else "sp_" + code

    def is_composed(self):

        """
            Determines if this complex agent is composed out of more
            atomic/structure agents
         :return: <bool>"""
        return len(self.agents) > 1

    def extend_signature(self, atomic_signature: dict, structure_signature: dict):
        """
        Extend given signatures by possibly new context.

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: updated signatures
        """
        for agent in self.agents:
            atomic_signature, structure_signature = agent.extend_signature(atomic_signature, structure_signature)
        return atomic_signature, structure_signature

    def compatible(self, other: 'Complex'):
        """
        Checks whether two Complexes are compatible.

        :param other: another Complex
        :return: True if they are compatible
        """
        if type(self) != type(other):
            return False
        if self == other:
            return True
        self_agents = collections.Counter(self.agents)
        other_agents = collections.Counter(other.agents)
        if self.compartment == other.compartment and sum(self_agents.values()) == sum(other_agents.values()):
            other_permutations = list(itertools.permutations(list(other_agents.elements())))
            for self_perm in itertools.permutations(list(self_agents.elements())):
                for other_perm in other_permutations:
                    if all([self_perm[i].compatible(other_perm[i]) for i in range(len(self_perm))]):
                        return True
        return False

    def identify_compatible(self, agents: tuple) -> list:
        """
        Identifies compatible agents from given list.

        :param agents: given tuple of agents (ordering)
        :return: list of indices of compatible agents
        """
        positions = []
        for i in range(len(agents)):
            if self.compatible(agents[i]):
                positions.append(i)
        return positions

    def reduce_context(self) -> 'Complex':
        """
        Reduces context of Complex to minimum.

        :return: new Complex with reduced context
        """
        new_agents = [agent.reduce_context() for agent in self.agents]
        return Complex(new_agents, self.compartment)

    def create_all_compatible(self, atomic_signature: dict, structure_signature: dict):
        """
        Creates all fully specified complexes compatible with the Complex

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: set of all create Complexes
        """
        results = []
        for agent in self.agents:
            agent_derivatives = agent.add_context(1, atomic_signature, structure_signature)
            results.append({pair[0] for pair in agent_derivatives})
        output_complexes = set()
        for result in itertools.product(*results):
            output_complexes.add(Complex(list(result), self.compartment))
        return output_complexes
