from scipy.integrate import odeint
import numpy as np
import pandas as pd
import random

from TS.State import State
from TS.TransitionSystem import TransitionSystem

AVOGADRO = 6.022 * 10**23


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

    def deterministic_simulation(self, max_time: float, volume: float) -> pd.DataFrame:
        """
        Translates model to ODE and runs odeint solver for given max_time.

        :param max_time: end time of simulation
        :param volume: volume of the system
        :return: simulated data
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
        y_0 = list(map(lambda x: x/(AVOGADRO * volume), self.init.sequence))
        y = odeint(fun, y_0, t)
        df = pd.DataFrame(data=y, columns=list(map(str, self.ordering)))
        df.insert(0, "times", t)
        return df

    def stochastic_simulation(self, max_time: float, runs: int) -> pd.DataFrame:
        """
        Gillespie algorithm implementation.

        Each step a random reaction is chosen by exponential distribution with density given as a sum
        of all possible rates in particular State.
        Then such reaction is applied and next time is computed using Poisson distribution (random.expovariate).

        :param max_time: time when simulation ends
        :param runs: how many time the process should be repeated (then average behaviour is taken)
        :return: simulated data
        """
        header = ["times"] + list(map(str, self.ordering))
        result_df = pd.DataFrame(columns=header)

        for run in range(runs):
            df = pd.DataFrame(columns=header)
            solution = self.init
            time = 0.0
            while time < max_time:
                # enumerate all rates
                applied_reactions = pd.DataFrame(data=[reaction.apply(solution, np.math.inf)
                                                       for reaction in self.vector_reactions],
                                                 columns=["state", "rate"])
                rates_sum = applied_reactions.sum()["rate"]
                sorted_applied = applied_reactions.sort_values(by=["rate"])
                sorted_applied["cumsum"] = sorted_applied.cumsum(axis=0)["rate"]

                # pick random reaction based on rates
                rand_number = rates_sum * random.random()
                sorted_applied.drop(sorted_applied[sorted_applied["cumsum"] < rand_number].index, inplace=True)
                solution = sorted_applied.iloc[0]["state"]

                # add to data
                df.loc[len(df)] = [time] + list(solution.sequence)

                # update time
                time += random.expovariate(rates_sum)

            if run != 0:
                averages = (df.stack() + result_df.stack()) / 2
                averages = averages.unstack()
                result_df = averages.dropna()[header]
            else:
                result_df = df
        return result_df

    def generate_transition_system(self) -> TransitionSystem:
        # reaction vectors have already replaced known parameters by their values
        # should be done in parallel

        # each time we encounter a new state (not present in encoding), add its new code and create edge between codes
        # -> a better version would be to use hash of State, but the numbers would be probably too huge for Storm
        # problem of checking whether State exists should be O(1) if State has good hash function

        # if case of getting above the bound, we should create special state with all element mth.inf
        pass