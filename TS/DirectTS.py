from sortedcontainers import SortedList
import json


class DirectTS:
    def __init__(self, bound):
        self.edges = set()
        self.unprocessed = set()
        self.processed = set()
        self.unique_complexes = set()
        self.init = None
        self.bound = bound

    def __str__(self):
        return str(self.processed) + "\n" + "\n".join(list(map(str, self.edges))) + "\n"

    def __repr__(self):
        return str(self)

    def save_to_json(self, output_file, params=None):
        ordering = SortedList(sorted(self.unique_complexes))
        # state -> unique ID
        states_encoding = self.create_encoding()
        # replace states to unique IDs in edges
        self.encode_edges(states_encoding)

        states = dict()
        for state in states_encoding:
            # unique ID -> numpy vector
            states[states_encoding[state]] = str(state.to_vector(ordering))

        unprocessed = dict()
        if self.unprocessed:
            for state in self.unprocessed:
                unprocessed[states_encoding[state]] = str(state.to_vector(ordering))

        init = states_encoding[self.init]
        save_to_json(states, unprocessed, self.edges, init, ordering, output_file, self.bound, params)

    def create_encoding(self):
        # for now assume generating is complete i.e. ignore unprocessed states
        states_encoding = dict()
        for state in self.processed | self.unprocessed:
            states_encoding[state] = len(states_encoding) + 1
        return states_encoding

    def encode_edges(self, states_encoding):
        for edge in self.edges:
            edge.encode(states_encoding)


def save_to_json(states, unprocessed, edges, init, ordering, output_file, bound, params):
    """
    Save current TS as a JSON file.

    :param output_file: given file to write to
    """
    unique = list(map(str, ordering))
    edges = [edge.to_dict() for edge in edges]
    data = {'nodes': states, 'edges': edges, 'ordering': unique, 'initial': init, 'bound': bound}
    if params:
        data['parameters'] = list(params)

    if unprocessed:
        data['unprocessed'] = unprocessed

    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)
