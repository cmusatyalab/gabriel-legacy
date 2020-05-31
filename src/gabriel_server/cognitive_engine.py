from abc import ABC
from abc import abstractmethod
from gabriel_protocol import gabriel_pb2


def wrong_input_format_message(frame_id):
    result_wrapper = gabriel_pb2.ResultWrapper()
    result_wrapper.frame_id = frame_id
    result_wrapper.status = gabriel_pb2.ResultWrapper.Status.WRONG_INPUT_FORMAT

    return result_wrapper


def unpack_extras(extras_class, from_client):
    extras = extras_class()
    from_client.extras.Unpack(extras)
    return extras


class Engine(ABC):
    @abstractmethod
    def handle(self, from_client):
        pass
