from abc import ABC
from abc import abstractmethod



def error_output(frame_id):
    output = gabriel_pb2.Output()
    output.status = gabriel_pb2.Output.Status.WRONG_INPUT_FORMAT


class Engine(ABC):
    @abstractmethod
    def handle(self, input):
        pass
