import logging
import zmq
from gabriel_protocol import gabriel_pb2


THREE_MINUTES = 180000
REQUEST_RETIRES = 3


logger = logging.getLogger(__name__)


def run(engine, filter_name, server_address, timeout=THREE_MINUTES,
        request_retries=REQUEST_RETRIES):
    context = zmq.Context()
    poll = zmq.Poller()

    while request_retries > 0:
        socket = context.socket(zmq.REQ)
        socket.connect(server_address)
        poll.register(socket, zmq.POLLIN)
        socket.send(filter_name.encode())
        logger.info('Sent welcome message to server')

        while True:
            responses = poll.poll(timeout)
            if len(responses) == 0:
                logger.warning('No response from server')
                socket.setsockopt(zmq.LINGER, 0)
                socket.close()
                poll.unregister(socket)
                request_retries -= 1
                break

            message_from_server = socket.recv()
            if message_from_server == ''b:
                # Heartbeat message
                socket.send(''b)
                continue

            from_client = gabriel_pb2.FromClient()
            from_client.ParseFromString(message_from_server)

            assert from_client.filter_passed == filter_name

            result_wrapper = engine.handle(from_client)
            socket.send(result_wrapper.SerializeToString())

    logger.warning('Ran out of retires. Abandoning server connection.')
