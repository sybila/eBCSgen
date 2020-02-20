class Edge:
    def __init__(self, source, target, probability):
        self.source = source
        self.target = target
        self.probability = probability

    def __hash__(self):
        return int(self.source * self.target * self.probability)

    def __eq__(self, other: 'Edge'):
        return self.source == other.source and self.target == other.target and self.probability == other.probability

    def __repr__(self):
        return str(self)

    def __str__(self):
        return " ".join(list(map(str, [self.source, self.target, self.probability])))
