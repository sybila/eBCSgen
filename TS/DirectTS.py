class DirectTS:
    def __init__(self):
        self.states_encoding = dict()  # State -> int
        self.edges = set()  # Edge objects: (int from, int to, probability), can be used for explicit Storm format
        self.init = None

        # for TS generating
        self.unprocessed = set()
        self.processed = set()

    def to_TS(self):
        pass
