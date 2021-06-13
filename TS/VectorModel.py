import multiprocessing

import time
from scipy.integrate import odeint
import numpy as np
import pandas as pd
import random
from sortedcontainers import SortedList

from TS.State import MemorylessState
from TS.TSworker import TSworker
from TS.TransitionSystem import TransitionSystem

AVOGADRO = 6.022 * 10 ** 23


def fake_expovariate(rate):
    return 0.1


def handle_number_of_threads(number, workers):
    """
    Estimated number of required workers for current volume of unprocessed states.

    :param number: volume of unprocessed states
    :param workers: available workers
    """
    number = np.math.ceil((1 / 50.0) * number - 1 / 2.)
    for (i, worker) in enumerate(workers):
        if i <= number:
            worker.work.set()
        else:
            worker.work.clear()


class VectorModel:
    def __init__(self, vector_reactions: set, init: MemorylessState, ordering: SortedList, bound: int):
        self.vector_reactions = vector_reactions
        self.init = init
        self.ordering = ordering
        self.bound = bound if bound else self.compute_bound()

    def __eq__(self, other: 'VectorModel') -> bool:
        return self.vector_reactions == other.vector_reactions and \
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

    def deterministic_simulation(self, max_time: float, volume: float, step: float = 0.01) -> pd.DataFrame:
        """
        Translates model to ODE and runs odeint solver for given max_time.

        :param max_time: end time of simulation
        :param volume: volume of the system
        :param step: distance between time points
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
                if reaction.source.sequence[i] > 0:
                    ODEs[i] += " - {}*({})".format(reaction.source.sequence[i], reaction.rate)
                    # positive effect
                if reaction.target.sequence[i] > 0:
                    ODEs[i] += " + {}*({})".format(reaction.target.sequence[i], reaction.rate)
        
        t = np.arange(0, max_time + step, step)
        y_0 = list(map(lambda x: x / (AVOGADRO * volume), self.init.sequence))
        y = odeint(fun, y_0, t)
        df = pd.DataFrame(data=y, columns=list(map(str, self.ordering)))
        df.insert(0, "times", t)
        return df

    def stochastic_simulation(self, max_time: float, runs: int, testing: bool = False) -> pd.DataFrame:
        """
        Gillespie algorithm implementation.

        Each step a random reaction is chosen by exponential distribution with density given as a sum
        of all possible rates in particular MemorylessState.
        Then such reaction is applied and next time is computed using Poisson distribution (random.expovariate).

        :param max_time: time when simulation ends
        :param runs: how many time the process should be repeated (then average behaviour is taken)
        :return: simulated data
        """
        header = list(map(str, self.ordering))
        result_df = pd.DataFrame(columns=header)

        if not testing:
            time_step = random.expovariate
        else:
            random.seed(10)
            time_step = fake_expovariate

        for run in range(runs):
            df = pd.DataFrame(columns=header, dtype=float)
            solution = self.init
            time = 0.0
            while time < max_time:
                # add to data
                df.loc[time] = list(solution.sequence)

                applied_reactions = pd.DataFrame(data=[reaction.apply(solution, np.math.inf)
                                                       for reaction in self.vector_reactions],
                                                 columns=["state", "rate"])
                applied_reactions = applied_reactions.dropna()
                if not applied_reactions.empty:
                    rates_sum = applied_reactions.sum()["rate"]
                    sorted_applied = applied_reactions.sort_values(by=["rate"])
                    sorted_applied["cumsum"] = sorted_applied.cumsum(axis=0)["rate"]

                    # pick random reaction based on rates
                    rand_number = rates_sum * random.random()
                    sorted_applied.drop(sorted_applied[sorted_applied["cumsum"] < rand_number].index, inplace=True)
                    solution = sorted_applied.iloc[0]["state"]
                else:
                    rates_sum = random.uniform(0.5, 0.9)

                # update time
                time += time_step(rates_sum)

            if run != 0:
                # union of the indexes
                union_idx = df.index.union(result_df.index)
                df = df.reindex(union_idx)
                result_df = result_df.reindex(union_idx)

                # interpolate both
                df = df.interpolate(method='linear', limit_direction='forward', axis=0)
                result_df = result_df.interpolate(method='linear', limit_direction='forward', axis=0)

                # concat both and compute average
                result_df = pd.concat([df, result_df])
                result_df = result_df.groupby(level=0).mean()
            else:
                result_df = df

        result_df.index.name = 'times'
        result_df.reset_index(inplace=True)
        return result_df

    def generate_transition_system(self, ts: TransitionSystem = None,
                                   max_time: float = np.inf, max_size: float = np.inf) -> TransitionSystem:
        """
        Parallel implementation of Transition system generating.

        The workload is distributed to Workers which take unprocessed States from the pool and process them.

        If the given bound should be exceeded, a special infinite state is introduced.

        The algorithm dynamically changes number of active workers using thread events. This is done according to the
        current volume of unprocessed states.

        :return: generated Transition system
        """
        if not ts:
            ts = TransitionSystem(self.ordering)
            ts.unprocessed = {self.init}

        workers = [TSworker(ts, self) for _ in range(multiprocessing.cpu_count())]
        for worker in workers:
            worker.start()

        workers[0].work.set()
        start_time = time.time()

        try:
            while any([worker.work.is_set() for worker in workers]) \
                    and time.time() - start_time < max_time \
                    and len(ts.processed) + len(ts.states_encoding) < max_size:
                handle_number_of_threads(len(ts.unprocessed), workers)
                time.sleep(1)
        # probably should be changed to a different exceptions for the case when the execution is stopped on Galaxy
        # then also the ts should be exported to appropriate file
        except (KeyboardInterrupt, EOFError) as e:
            pass

        for worker in workers:
            worker.join()

        while any([worker.is_alive() for worker in workers]):
            time.sleep(1)

        ts.encode(self.init)

        return ts
