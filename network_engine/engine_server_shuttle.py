import logging
from threading import Thread
from gabriel_server.client_comm import WebsocketServer
from gabriel_server import gabriel_pb2
from gabriel_server import cognitive_engine
import zmq


ENGINE_ADDR = 'tcp://*:5555'


logger = logging.getLogger(__name__)


def _engine_comm(websocket_server, engine_addr=ENGINE_ADDR):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(engine_addr)

    engine_name = socket.recv_string()
    logging.info('Connected to %s engine', engine_name)

    while True:
        engine_server = gabriel_pb2.EngineServer()
        engine_server.ParseFromString(websocket_server.input_queue.get())
        from_client = gabriel_pb2.FromClient()
        from_client.ParseFromString(engine_server.serialized_proto)

        if from_client.engine == engine_name:
            socket.send(engine_server.serialized_proto)
            serialized_result = socket.recv()
        else:
            serialized_result = cognitive_engine.engine_not_available_message(
                from_client.frame_id).SerializeToString()

        address = (engine_server.host, engine_server.port)
        websocket_server.submit_result(serialized_result, address)


def run():
    '''This should never return'''
    websocket_server = WebsocketServer()

    engine_comm_thread = Thread(
        target=_engine_comm,
        args=(websocket_server,))
    engine_comm_thread.start()

    websocket_server.launch()
    logger.error('Got to end of run')
