from abc import ABC
from abc import abstractmethod

class Engine(ABC):
    @abstractmethod
    def handle(self, input):
        pass
