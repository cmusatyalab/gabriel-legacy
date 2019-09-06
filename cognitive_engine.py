from abc import ABC
from abc import abstractmethod



def wrong_input_format_error(frame_id):
    from_server = gabriel_pb2.FromServer()
    from_server.status = gabriel_pb2.FromServer.Status.WRONG_INPUT_FORMAT

    return from_server


class Engine(ABC):
    @abstractmethod
    def handle(self, input):
        pass
