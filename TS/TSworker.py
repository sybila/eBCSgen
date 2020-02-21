import threading

from TS.Edge import Edge


class TSworker(threading.Thread):
    def __init__(self, ts, states_to_process, model):
        super(TSworker, self).__init__()
        self.ts = ts  # resulting transition system
        self.states_to_process = states_to_process  # pile of states to be processed, shared with all the processes
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
        """
        while not self.stop_request.isSet():
            self.work.wait()
            try:
                state = self.states_to_process.pop()
                for reaction in self.model.vector_reactions:
                    new_state, rate = reaction.apply(state, self.model.bound)
                    if new_state:
                        if new_state not in self.ts.states_encoding:
                            self.states_to_process.add(new_state)
                        source = self.ts.get_state_encoding(state)
                        self.ts.edges.add(Edge(source, self.ts.get_state_encoding(new_state), rate))
            except KeyError:
                continue

    def join(self, timeout=None):
        self.work.set()
        self.stop_request.set()
