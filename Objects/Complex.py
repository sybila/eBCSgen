import collections


class Complex:
    def __init__(self, agents: collections.Counter, compartment: str):
        self.agents = agents
        self.compartment = compartment

    def __repr__(self):
        return str(self)

    def __str__(self):
        return ".".join(list(map(str, sorted(list(self.agents.elements()))))) + "::" + self.compartment

    def __lt__(self, other: 'Complex'):
        return str(self) < str(other)

    def __eq__(self, other: 'Complex'):
        return self.compartment == other.compartment and self.agents == other.agents

    def __hash__(self):
        return hash(str(self))

    def compatible(self, other: 'Complex'):
        if type(self) != type(other):
            return False
        if self == other:
            return True
        if self.compartment == other.compartment and sum(self.agents.values()) == sum(other.agents.values()):
            pass
        return False
