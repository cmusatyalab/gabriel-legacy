import logging
import zmq


logger = logging.getLogger(__name__)


def run(engine_setup, addr):
    engine = engine_setup()
    logger.info('Cognitive engine started')
    socket = context.socket(zmq.REQ)
    socket.connect(addr)

    socket.send_string(engine.name)

    logger.info('Waiting for input')
    while True:
        from_client = gabriel_pb2.FromClient()
        from_client.ParseFromString(socket.recv())
        logging.debug('Received input')

        from_server = engine.handle(from_client)
        socket.send(from_server.SerializeToString())
