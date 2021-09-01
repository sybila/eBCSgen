from sortedcontainers import SortedList
import json

from TS.TransitionSystem import TransitionSystem


class DirectTS:
    def __init__(self):
        self.edges = set()
        self.unprocessed = set()
        self.processed = set()
        self.unique_complexes = set()
        self.init = None
        self.bound = None

    def __str__(self):
        return str(self.processed) + "\n" + "\n".join(list(map(str, self.edges))) + "\n"

    def __repr__(self):
        return str(self)

    def save_to_json(self, output_file, params=None):
        ts = self.to_vector_ts()
        ts.save_to_json(output_file, params)

    def to_vector_ts(self):
        ordering = SortedList(sorted(self.unique_complexes))
        # state -> unique ID
        states_encoding = self.create_encoding()
        # replace states to unique IDs in edges
        self.encode_edges(states_encoding)

        states = dict()
        for state in states_encoding:
            # unique ID -> numpy vector
            states[state.to_vector(ordering)] = states_encoding[state]

        unprocessed = dict()
        if self.unprocessed:
            for state in self.unprocessed:
                unprocessed[state.to_vector(ordering)] = states_encoding[state]

        ts = TransitionSystem(ordering, self.bound)
        ts.states_encoding = states
        ts.edges = self.edges
        ts.init = states_encoding[self.init]
        ts.unprocessed = unprocessed
        return ts

    def create_encoding(self):
        # for now assume generating is complete i.e. ignore unprocessed states
        states_encoding = dict()
        for state in self.processed | self.unprocessed:
            states_encoding[state] = len(states_encoding) + 1
        return states_encoding

    def encode_edges(self, states_encoding):
        for edge in self.edges:
            edge.encode(states_encoding)
