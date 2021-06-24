from abc import ABC, abstractmethod


class BaseRegulation(ABC):
    def __init__(self, regulation):
        self.regulation = regulation

    @abstractmethod
    def filter(self, current_state, candidates):
        pass
