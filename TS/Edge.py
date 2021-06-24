class Edge:
    def __init__(self, source, target, probability, label=None, encoded=False):
        self.source = source
        self.target = target
        self.probability = probability
        self.label = label
        self._is_encoded = encoded

    def __hash__(self):
        return hash((self.source, self.target, self.probability))

    def __eq__(self, other: 'Edge'):
        return self.source == other.source and self.target == other.target and self.probability == other.probability

    def __lt__(self, other: 'Edge'):
        if self.source != other.source:
            return self.source < other.source
        else:
            return self.target < other.target

    def __repr__(self):
        return str(self)

    def __str__(self):
        return " ".join(list(map(str, [self.source, self.target, self.probability])))

    def encode(self, encoding):
        if not self._is_encoded:
            self.source = encoding[self.source]
            self.target = encoding[self.target]
            self._is_encoded = True

    def recode(self, encoding_old: dict, encoding_new: dict) -> 'Edge':
        """
        Recodes the edge to new encoding

        :param encoding_old: the old encoding
        :param encoding_new: the new encoding
        :return: new Edge in new encoding
        """
        return Edge(encoding_new[encoding_old[self.source]],
                    encoding_new[encoding_old[self.target]],
                    self.probability)

    def add_rate(self, rate):
        """
        Adds given rate to self.probability.

        Used when joining two Edges between the same nodes.

        :param rate: given rate expression
        """
        self.probability += rate

    def normalise(self, factor):
        """
        Normalises rate to probability and converts it to float or string
        (depending on parameters presence).

        :param factor: given sum of all rates
        """
        try:
            self.probability = float(self.probability)
            self.probability /= float(factor)
        except TypeError:
            self.probability = "(" + str(self.probability) + ")/(" + str(factor) + ")"

    def to_dict(self):
        """
        Exports the edge as a dict.

        :return: dict representing the edge
        """
        result = {'s': self.source, 't': self.target, 'p': self.probability}
        if self.label:
            result['label'] = self.label
        return result

    def to_PRISM_string(self, decoding) -> str:
        """
        Creates string representation for PRISM file.

        :return: PRISM string representation
        """
        return str(self.probability) + " : " + decoding[self.target].to_PRISM_string(True)

    def to_vector(self, ordering):
        source = self.source.to_vector(ordering)
        target = self.target.to_vector(ordering)
        return Edge(source, target, self.probability)


def edge_from_dict(d: dict) -> Edge:
    """
    Creates edge from given dict.

    :param d: dict representing the edge
    :return: Edge
    """
    return Edge(d['s'], d['t'], d['p'], True)
