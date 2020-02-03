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
