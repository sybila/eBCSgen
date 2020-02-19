from scipy.integrate import odeint
import numpy as np
import pandas as pd

from TS.State import State


class VectorModel:
    def __init__(self, vector_reactions: set, init: State, ordering: tuple, bound: int):
        self.vector_reactions = vector_reactions
        self.init = init
        self.ordering = ordering
        self.bound = bound if bound else self.compute_bound()

    def __eq__(self, other: 'VectorModel') -> bool:
        return self.vector_reactions == other.vector_reactions and\
               self.init == other.init and self.ordering == other.ordering

    def __str__(self):
        return "Vector model:\n" + "\n".join(map(str, sorted(self.vector_reactions))) + "\n\n" \
               + str(self.init) + "\n\n" + str(self.ordering)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    def compute_bound(self):
        """
        Computes maximal bound from all reactions and initial state.

        :return: maximal bound
        """
        reation_max = max(map(lambda r: max(max(r.source.sequence), max(r.target.sequence)), self.vector_reactions))
        return max(reation_max, max(self.init.sequence))

    def generate_transition_system(self) -> State:
        # reaction vectors have already replaced known parameters by their values
        # should be done in parallel
        pass

    def deterministic_simulation(self, max_time: float, volume: float) -> pd.DataFrame:
        """
        Translates model to ODE and runs odeint solver for given max_time.

        :param max_time: end time of simulation
        :param volume: volume of the system
        :param output_file: name of output file
        """

        def fun(y, t):
            """
            Function used in odeint solver. See its docs for more info.
            It uses global variable ODEs in local scope of the method.

            :param y: data points
            :param t: time points
            """
            return list(map(eval, ODEs))

        ODEs = [""] * len(self.init)
        for reaction in self.vector_reactions:
            reaction.to_symbolic()
            for i in range(len(self.init)):
                # negative effect
                if reaction.source.sequence[i] == 1:
                    ODEs[i] += " - " + str(reaction.rate)
                # positive effect
                if reaction.target.sequence[i] == 1:
                    ODEs[i] += " + " + str(reaction.rate)
        t = np.arange(0, max_time, 0.01)
        y_0 = list(self.init.sequence)
        y = odeint(fun, y_0, t)
        df = pd.DataFrame(data=y, columns=list(map(str, self.ordering)))
        df.insert(0, "times", t)
        return df

    def stochastic_simulation(self, options) -> list:
        # Gillespie algorithm
        pass

    def write_output(self, data, times, output_file):
        output = open(output_file, "w")
        header = ["times"] + list(map(str, self.ordering))
        output.write(",".join(header) + "\n")
        for i in range(len(data)):
            output.write(str(times[i]) + "," + ",".join(list(map(str, data[i]))) + "\n")
        output.close()
