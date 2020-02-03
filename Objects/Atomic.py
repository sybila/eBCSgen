class AtomicAgent:
    def __init__(self, name: str, state: str):
        self.name = name
        self.state = state

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name + "{" + self.state + "}"

    def __lt__(self, other: 'AtomicAgent'):
        return self.name < other.name

    def __eq__(self, other: 'AtomicAgent'):
        if type(self) != type(other):
            return False
        return self.name == other.name and self.state == other.state

    def __hash__(self):
        return hash(str(self))

    def compatible(self, other: 'AtomicAgent') -> bool:
        if type(self) != type(other):
            return False
        return (self == other) or (self.name == other.name and self.state == "_")

    def add_context(self, other, atomic_signature: dict, structure_signature: dict) -> set:
        """
        Fills missing context for given agent.

        If other is also an atomic agents, this methods gives them both the same states
         according to the given atomic_signature.
        Otherwise, context is filled independently and other part is None.
        Finally, if both agents have defined states, they are returned untouched.

        Note: it is assumed this method is used only for well formed rules, which means
         given atomics have the same name AND either both do or do not have specified state.

        :param other: possibly an atomic agent, -1 if context is empty on left, 1 for right
        :param atomic_signature: given mapping of atomic name to possible states
        :param structure_signature: given mapping of structure name to possible atomics
        :return: set of pairs
        """
        if type(self) == type(other):
            if self.state == "_" and other.state == "_":
                result = set()
                for state in atomic_signature[self.name]:
                    result.add((AtomicAgent(str(self.name), state), AtomicAgent(str(self.name), state)))
                return result
            else:
                return {(self, other)}
        result = set()
        if other == -1:
            for state in atomic_signature[self.name]:
                result.add((None, AtomicAgent(str(self.name), state)))
        else:
            for state in atomic_signature[self.name]:
                result.add((AtomicAgent(str(self.name), state), None))
        return result
