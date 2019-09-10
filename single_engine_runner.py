import logging
from multiprocessing import Process
from multiprocessing import Pipe
from threading import Thread
from gabriel_server.client_comm import WebsocketServer
from gabriel_server import gabriel_pb2


logger = logging.getLogger(__name__)


def _engine_not_available_message(frame_id):
    from_server = gabriel_p2.FromServer()
    from_server.frame_id = frame_id
    from_server.status = (
        gabriel_pb2.FromServer.Status.REQUESTED_ENGINE_NOT_AVAILABLE)
    return from_server


def _run_engine(engine_setup, input_queue, conn):
    engine = engine_setup()
    logger.info('Cognitive engine started')
    while True:
        engine_server = gabriel_pb2.EngineServer()
        engine_server.ParseFromString(input_queue.get())
        from_client = gabriel_pb2.FromClient()
        from_client.ParseFromString(engine_server.serialized_proto)

        if from_client.engine == engine.proto_engine:
            from_server = engine.handle(from_client)
        else:
            from_server = _engine_not_available_message(
                from_client.frame_id)

        engine_server.serialized_proto = (
            from_server.SerializeToString())
        conn.send(engine_server.SerializeToString())


def _queue_shuttle(websocket_server, conn):
    '''Add results to the output queue when they become available.

    We cannot add a coroutine to an event loop from a different process.
    Therefore, we need to run this in a different thread within the process
    running the event loop.'''

    while True:
        engine_server = gabriel_pb2.EngineServer()
        engine_server.ParseFromString(conn.recv())
        address = (engine_server.host, engine_server.port)

        websocket_server.submit_result(
            engine_server.serialized_proto, address)


def run(engine_setup):
    '''This should never return'''
    websocket_server = WebsocketServer()

    parent_conn, child_conn = Pipe()
    shuttle_thread = Thread(
        target=_queue_shuttle,
        args=(websocket_server, parent_conn))
    shuttle_thread.start()
    engine_process = Process(
        target=_run_engine,
        args=(engine_setup, websocket_server.input_queue, child_conn))
    engine_process.start()

    websocket_server.launch()
    logger.error('Got to end of run')
