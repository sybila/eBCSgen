import threading

import time


class TSworker(threading.Thread):
    def __init__(self, ts, model):
        super(TSworker, self).__init__()
        self.ts = ts  # resulting transition system
        self.model = model

        self.stop_request = threading.Event()
        self.work = threading.Event()  # to control whether the Worker is supposed to work

    def run(self):
        """
        Method takes a state from pool of states to be processed and:
        1. iteratively applies all reactions on it
        2. checks whether newly created state (if any) was already processed (present in self.ts.states_encoding)
           2.1 if not, it is added to self.states_to_process
        3. creates Edge from the source state to created one (since ts.edges is a set, we don't care about its presence)
        4. all outgoing Edges from the state are normalised to probability
        """
        while not self.stop_request.isSet():
            self.work.wait()
            try:
                state = self.ts.unprocessed.pop()
                edges = set()

                # special "hell" state
                if state.is_inf:
                    edge = self.ts.new_edge(state, state, 1)
                    self.ts.edges.add(edge)
                else:
                    for reaction in self.model.vector_reactions:
                        new_state, rate = reaction.apply(state, self.model.bound)
                        if new_state and rate:
                            if new_state not in self.ts.states_encoding:
                                self.ts.unprocessed.add(new_state)
                            edges.add(self.ts.new_edge(state, new_state, rate))

                    # normalise
                    factor = sum(list(map(lambda edge: edge.probability, edges)))
                    for edge in edges:
                        edge.normalise(factor)
                        self.ts.edges.add(edge)

            except KeyError:
                self.work.clear()

    def join(self, timeout=None):
        self.work.set()
        self.stop_request.set()
