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

    def add_context(self, other, atomic_signature: dict, structure_signature: dict) -> set:
        """
        Fills missing context for given agent.

        ...

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


        result = set()
        if other == -1:
            pass
        else:
            pass
        return result