import logging
import zmq
from gabriel_server import gabriel_pb2


logger = logging.getLogger(__name__)


def run(engine_setup, engine_name, addr):
    engine = engine_setup()
    logger.info('Cognitive engine started')

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(addr)

    socket.send_string(engine_name)

    logger.info('Waiting for input')
    while True:
        from_client = gabriel_pb2.FromClient()
        from_client.ParseFromString(socket.recv())
        logging.debug('Received input')

        result_wrapper = engine.handle(from_client)

        socket.send(result_wrapper.SerializeToString())
