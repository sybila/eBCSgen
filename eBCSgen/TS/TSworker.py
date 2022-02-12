import threading

from eBCSgen.TS.Edge import Edge


class TSworker(threading.Thread):
    def __init__(self, ts, reactions, definitions, regulation):
        super(TSworker, self).__init__()
        self.ts = ts  # resulting transition system
        self.reactions = reactions
        self.definitions = definitions  # model.definitions
        self.regulation = regulation  # model.regulation

        self.stop_request = threading.Event()
        self.work = threading.Event()  # to control whether the Worker is supposed to work

    def run(self):
        """
        Method takes a state from pool of states to be states and:
        1. iteratively applies all rules on it
        2. checks whether newly created states (if any) were already states (present in self.ts.states_encoding)
        2.1 if not, it is added to self.states_to_process
        3. creates Edge from the source state to created ones (since ts.edges is a set, we don't care about its presence)
        4. all outgoing Edges from the state are normalised to probability
        """
        while not self.stop_request.isSet():
            self.work.wait()
            try:
                state = self.ts.unprocessed.pop()
                self.ts.states.add(state)
                unique_states = dict()

                # special "hell" state
                if state.is_hell:
                    self.ts.edges.add(Edge(state, state, 1))
                else:
                    candidate_reactions = dict()
                    for reaction in self.reactions:
                        rate = reaction.evaluate_rate(state, self.definitions)
                        matches = reaction.match(state, all=True)

                        try:
                            rate = rate if rate > 0 else None
                        except TypeError:
                            pass

                        # drop rules which cannot be actually used (0 rate or no matches)
                        if matches is not None and rate is not None:
                            candidate_reactions[reaction] = (rate, matches)

                    if self.regulation:
                        candidate_reactions = self.regulation.filter(state, candidate_reactions)

                    for reaction in candidate_reactions.keys():
                        for match in candidate_reactions[reaction][1]:
                            produced_agents = reaction.replace(match)
                            match = reaction.reconstruct_complexes_from_match(match)
                            new_state = state.update_state(match, produced_agents, reaction.label, self.ts.bound)

                            if new_state not in self.ts.states:
                                self.ts.unprocessed.add(new_state)
                                self.ts.unique_complexes.update(set(new_state.content.value))

                            # multiple arrows between two states are not allowed
                            if new_state in unique_states:
                                unique_states[new_state].add_rate(candidate_reactions[reaction][0])
                            else:
                                edge = Edge(state, new_state, candidate_reactions[reaction][0], reaction.label)
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
