import itertools
from copy import deepcopy

from eBCSgen.Core.Atomic import AtomicAgent


class StructureAgent:
    def __init__(self, name: str, composition: set):
        self.name = name
        self.composition = composition

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name + "(" + ",".join(list(map(str, sorted(self.composition)))) + ")"

    def __lt__(self, other: 'StructureAgent'):
        return str(self) < str(other)

    def __eq__(self, other: 'StructureAgent'):
        if type(self) != type(other):
            return False
        return self.name == other.name and self.composition == other.composition

    def __hash__(self):
        return hash(str(self))

    def compatible(self, other: 'StructureAgent'):
        """
        This methods works correctly because it is guaranteed
        that each atomic agent name is at most once in the composition.

        :param other: another StructureAgent
        :return: True if they are compatible
        """
        if type(self) != type(other):
            return False
        if self == other:
            return True
        if other.name != self.name:
            return False
        for self_atomic in self.composition:
            found_pair = False
            for other_atomic in other.composition:
                if self_atomic.compatible(other_atomic):
                    found_pair = True
            if not found_pair:
                return False
        return True

    def extend_signature(self, atomic_signature: dict, structure_signature: dict):
        """
        Extend given signatures by possibly new context.

        :param atomic_signature: given atomic signature
        :param structure_signature: given structure signature
        :return: updated signatures
        """
        if not self.composition:
            structure_signature[self.name] = structure_signature.get(self.name, set())
        else:
            for atomic in self.composition:
                structure_signature[self.name] = structure_signature.get(self.name, set()) | {atomic.name}
                atomic_signature, structure_signature = atomic.extend_signature(atomic_signature, structure_signature)
        return atomic_signature, structure_signature

    def add_context(self, other, atomic_signature: dict, structure_signature: dict) -> set:
        """
        Fills missing context for given agent.

        Note: it is assumed this method is used only for well formed rules, which means
        given structure agents have specified the same atomic agents and miss the same
        atomic agents.

        Moreover, agents which are not specified are completely omitted. TBD: this could be
        somehow hacked.

        :param other: possibly a structure agent, -1 if context is empty on left, 1 for right
        :param atomic_signature: given mapping of atomic name to possible states
        :param structure_signature: given mapping of structure name to possible atomics
        :return: set of pairs
        """
        present_atomics = set(map(lambda a: a.name, self.composition))
        if type(self) == type(other):
            if structure_signature[self.name] - present_atomics != set():
                result = []
                for atomic_name in structure_signature[self.name] - present_atomics:
                    possibilities = AtomicAgent(atomic_name, "_").add_context(AtomicAgent(atomic_name, "_"),
                                                                              atomic_signature, structure_signature)
                    result.append(possibilities)
                agents = set()
                for options in itertools.product(*result):
                    new_agent_self = StructureAgent(self.name, set(self.composition))
                    new_agent_other = StructureAgent(other.name, set(other.composition))
                    for (left, right) in options:
                        new_agent_self.composition.add(left)
                        new_agent_other.composition.add(right)
                    agents.add((new_agent_self, new_agent_other))
                return agents
            else:
                return {(self, other)}

        if structure_signature[self.name] - present_atomics != set():
            result = []
            for atomic_name in structure_signature[self.name] - present_atomics:
                possibilities = AtomicAgent(atomic_name, "_").add_context(1, atomic_signature, structure_signature)
                result.append(possibilities)
            agents = set()
            for options in itertools.product(*result):
                new_agent = StructureAgent(self.name, set(self.composition))
                for (left, right) in options:
                    new_agent.composition.add(left)
                if other == -1:
                    agents.add((None, new_agent))
                else:
                    agents.add((new_agent, None))
            return agents
        else:
            return {(None, self)} if other == -1 else {(self, None)}

    def reduce_context(self):
        """
        Reduces context of StructureAgent to minimum.

        :return: new StructureAgent with reduced context
        """
        return StructureAgent(self.name, set())

    def replace(self, agent):
        """
        Replace agent based on a pattern.

        :param agent: given agent to be changed
        :return: changed agent
        """
        result = set()
        for other_atomic in agent.composition:
            match = False
            for self_atomic in self.composition:
                if other_atomic.name == self_atomic.name:
                    result.add(self_atomic.replace(other_atomic))
                    match = True
            if not match:
                result.add(deepcopy(other_atomic))
        return StructureAgent(self.name, result)
