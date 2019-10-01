import logging
from threading import Thread
from gabriel_server.client_comm import WebsocketServer
from gabriel_server import gabriel_pb2
import zmq


ENGINE_ADDR = 'tcp://*:5555'


logger = logging.getLogger(__name__)


def _engine_comm(websocket_server, engine_addr=ENGINE_ADDR):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(engine_addr)

    logger.info('Waiting for engine')

    engine_name = socket.recv_string()
    logger.info('Connected to %s engine', engine_name)
    websocket_server.register_engine(engine_name)

    try:
        while True:
            to_from_engine = gabriel_pb2.ToFromEngine()
            to_from_engine.ParseFromString(websocket_server.input_queue.get())

            socket.send(to_from_engine.from_client.SerializeToString())
            serialized_result_wrapper = socket.recv()

            address = (to_from_engine.host, to_from_engine.port)
            result_wrapper = gabriel_pb2.ResultWrapper()
            result_wrapper.ParseFromString(serialized_result_wrapper)
            websocket_server.submit_result(result_wrapper, address)
    finally:
        logger.info('Server stopping')
        websocket_server.unregister_engine(engine_name)


def run():
    '''This should never return'''
    websocket_server = WebsocketServer()

    engine_comm_thread = Thread(
        target=_engine_comm,
        args=(websocket_server,))
    engine_comm_thread.start()

    websocket_server.launch()
    logger.error('Got to end of run')
