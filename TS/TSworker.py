import threading
import pandas as pd

from TS.Edge import Edge


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
                self.ts.processed.add(state)
                unique_states = dict()

                # special "hell" state
                if state.is_inf:
                    self.ts.edges.add(Edge(state, state, 1))
                else:
                    for reaction in self.model.vector_reactions:
                        new_state, rate = reaction.apply(state, self.model.bound)
                        if new_state and rate:
                            if new_state not in self.ts.processed:
                                self.ts.unprocessed.add(new_state)

                            # multiple arrows between two states are not allowed
                            if new_state in unique_states:
                                unique_states[new_state].add_rate(rate)
                            else:
                                edge = Edge(state, new_state, rate)
                                unique_states[new_state] = edge

                    edges = set(unique_states.values())

                    # normalise
                    factor = sum(list(map(lambda edge: edge.probability, edges)))
                    if edges:
                        for edge in edges:
                            edge.normalise(factor)
                            self.ts.edges.add(edge)
                    else:
                        # self loop to create correct DTMC
                        self.ts.edges.add(Edge(state, state, 1))

            except KeyError:
                self.work.clear()

    def join(self, timeout=None):
        self.work.set()
        self.stop_request.set()


class DirectTSworker(threading.Thread):
    def __init__(self, ts, model):
        super(DirectTSworker, self).__init__()
        self.ts = ts  # resulting transition system
        self.model = model

        self.stop_request = threading.Event()
        self.work = threading.Event()  # to control whether the Worker is supposed to work

    def run(self):
        """
        Method takes a state from pool of states to be processed and:
        1. iteratively applies all rules on it
        2. checks whether newly created states (if any) were already processed (present in self.ts.states_encoding)
           2.1 if not, it is added to self.states_to_process
        3. creates Edge from the source state to created ones (since ts.edges is a set, we don't care about its presence)
        4. all outgoing Edges from the state are normalised to probability
        """
        while not self.stop_request.isSet():
            self.work.wait()
            try:
                state = self.ts.unprocessed.pop()
                self.ts.processed.add(state)
                unique_states = dict()

                # special "hell" state
                if state.is_inf:
                    self.ts.edges.add(Edge(state, state, 1))
                else:
                    candidate_rules = dict()
                    for rule in self.model.rules:
                        candidate_rules[rule] = (rule.evaluate_rate(state, self.model.definitions),
                                                 rule.match(state, all=True))
                        # drop rules which cannot be actually used (0 rate or no matches)
                        candidate_rules = dict(filter(lambda item: item[1][0] > 0 and item[1][1] is not None,
                                                      candidate_rules.items()))

                    applicable_rules = self.model.regulation.filter(state, candidate_rules)

                    # TODO: bound is not included !

                    for rule in applicable_rules.keys():
                        for match in applicable_rules[rule][1]:
                            produced_agents = rule.replace(match)
                            match = rule.reconstruct_complexes_from_match(match)
                            new_state = state.update_state(match, produced_agents, rule.label)

                            if new_state not in self.ts.processed:
                                self.ts.unprocessed.add(new_state)
                                self.ts.unique_complexes.update(set(new_state.multiset))

                            # multiple arrows between two states are not allowed
                            if new_state in unique_states:
                                unique_states[new_state].add_rate(applicable_rules[rule][0])
                            else:
                                edge = Edge(state, new_state, applicable_rules[rule][0], rule.label)
                                unique_states[new_state] = edge

                    edges = set(unique_states.values())

                    # normalise
                    factor = sum(list(map(lambda edge: edge.probability, edges)))
                    if edges:
                        for edge in edges:
                            edge.normalise(factor)
                            self.ts.edges.add(edge)
                    else:
                        # self loop to create correct DTMC
                        self.ts.edges.add(Edge(state, state, 1, 'ε'))

            except KeyError:
                self.work.clear()

    def join(self, timeout=None):
        self.work.set()
        self.stop_request.set()
