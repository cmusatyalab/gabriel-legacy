import logging
import zmq
from gabriel_protocol import gabriel_pb2


logger = logging.getLogger(__name__)


def run(engine, filter_name, server_address):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect(server_address)

    socket.send(filter_name.encode())
    while True:
        from_client = gabriel_pb2.FromClient()
        from_client.ParseFromString(socket.recv())

        assert from_client.filter_passed == filter_name

        result_wrapper = engine.handle(from_client)
        socket.send(result_wrapper)
