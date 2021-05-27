from sortedcontainers import SortedList


from TS.TransitionSystem import TransitionSystem


class DirectTS:
    def __init__(self):
        self.edges = set()
        self.unprocessed = set()
        self.processed = set()
        self.unique_complexes = set()

    def __str__(self):
        return str(self.processed) + "\n" + "\n".join(list(map(str, self.edges))) + "\n"

    def __repr__(self):
        return str(self)

    def to_TS(self, init):
        ordering = SortedList(sorted(self.unique_complexes))
        states = set()
        for state in self.processed:
            states.add(state.to_vector(ordering))

        edges = set()
        for edge in self.edges:
            edges.add(edge.to_vector(ordering))

        ts = TransitionSystem(ordering)
        ts.edges = edges
        ts.processed = states
        ts.init = init.to_vector(ordering)
        return ts
