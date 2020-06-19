import logging
import zmq
from gabriel_protocol import gabriel_pb2
from gabriel_server import network_engine


TEN_SECONDS = 10000
REQUEST_RETRIES = 3


logger = logging.getLogger(__name__)


def run(engine, filter_name, server_address, timeout=TEN_SECONDS,
        request_retries=REQUEST_RETRIES):
    context = zmq.Context()

    while request_retries > 0:
        socket = context.socket(zmq.REQ)
        socket.connect(server_address)
        to_server_runner = gabriel_pb2.ToServerRunner()
        to_server_runner.welcome.filter_name = filter_name
        socket.send(to_server_runner.SerializeToString())
        logger.info('Sent welcome message to server')

        while True:
            if socket.poll(timeout) == 0:
                logger.warning('No response from server')
                socket.setsockopt(zmq.LINGER, 0)
                socket.close()
                request_retries -= 1
                break

            message_from_server = socket.recv()
            if message_from_server == network_engine.HEARTBEAT:
                socket.send(network_engine.HEARTBEAT)
                continue

            from_client = gabriel_pb2.FromClient()
            from_client.ParseFromString(message_from_server)

            assert from_client.filter_passed == filter_name

            to_server_runner = gabriel_pb2.ToServerRunner()
            result_wrapper = engine.handle(from_client)
            to_server_runner.result_wrapper.CopyFrom(result_wrapper)
            socket.send(to_server_runner.SerializeToString())

    logger.warning('Ran out of retires. Abandoning server connection.')
