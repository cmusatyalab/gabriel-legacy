from abc import ABC
from abc import abstractmethod
from gabriel_protocol import gabriel_pb2


def error_result_wrapper(frame_id, status, filter_passed):
    result_wrapper = gabriel_pb2.ResultWrapper()
    result_wrapper.frame_id = frame_id
    result_wrapper.status = status
    result_wrapper.filter_passed = filter_passed

    return result_wrapper


def pack_from_engine(host, port, result_wrapper, return_token=True):
    from_engine = gabriel_pb2.FromEngine()
    from_engine.host = host
    from_engine.port = port
    from_engine.return_token = return_token
    from_engine.result_wrapper.CopyFrom(result_wrapper)

    return from_engine


def unpack_extras(extras_class, from_client):
    extras = extras_class()
    from_client.extras.Unpack(extras)
    return extras


class Engine(ABC):
    @abstractmethod
    def handle(self, from_client):
        pass
