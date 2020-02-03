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
