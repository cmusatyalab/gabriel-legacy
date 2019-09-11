from abc import ABC
from abc import abstractmethod
from gabriel_server import gabriel_pb2


def _status_message(frame_id, status):
    content = gabriel_pb2.ToClient.Content()
    content.frame_id = frame_id
    content.status = status

    return content


def wrong_input_format_message(frame_id):
    return _status_message(
        frame_id, gabriel_pb2.ToClient.Content.Status.WRONG_INPUT_FORMAT)


def engine_not_available_message(frame_id):
    return _status_message(
        frame_id,
        gabriel_pb2.ToClient.Content.Status.REQUESTED_ENGINE_NOT_AVAILABLE)


def unpack_engine_fields(engine_fields_class, from_client):
    engine_fields = engine_fields_class()
    from_client.engine_fields.Unpack(engine_fields)
    return engine_fields


class Engine(ABC):
    @abstractmethod
    def handle(self, from_client):
        pass
