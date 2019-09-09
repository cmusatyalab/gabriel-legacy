from abc import ABC
from abc import abstractmethod
from gabriel_server import gabriel_pb2


def wrong_input_format_error(frame_id):
    from_server = gabriel_pb2.FromServer()
    from_server.frame_id = frame_id
    from_server.status = gabriel_pb2.FromServer.Status.WRONG_INPUT_FORMAT

    return from_server


class Engine(ABC):
    @property
    @abstractmethod
    def proto_engine(self):
        '''The gabriel_pb2.Engine value correspoinding to this cognitive
        engine'''
        pass

    @abstractmethod
    def handle(self, from_client):
        pass
