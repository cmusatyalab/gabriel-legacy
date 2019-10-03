import logging
from multiprocessing import Process
from multiprocessing import Pipe
from threading import Thread
from gabriel_server.client_comm import WebsocketServer
from gabriel_server import gabriel_pb2


logger = logging.getLogger(__name__)


def _run_engine(engine_setup, input_queue, conn):
    engine = engine_setup()
    logger.info('Cognitive engine started')
    while True:
        to_from_engine = gabriel_pb2.ToFromEngine()
        to_from_engine.ParseFromString(input_queue.get())

        result_wrapper = engine.handle(to_from_engine.from_client)

        # This cuases to_from_engine.from_client to be overwritten
        to_from_engine.result_wrapper.CopyFrom(result_wrapper)

        conn.send(to_from_engine.SerializeToString())


def _queue_shuttle(websocket_server, conn):
    '''Add results to the output queue when they become available.

    We cannot add a coroutine to an event loop from a different process.
    Therefore, we need to run this in a different thread within the process
    running the event loop.'''

    while True:
        to_from_engine = gabriel_pb2.ToFromEngine()
        to_from_engine.ParseFromString(conn.recv())
        address = (to_from_engine.host, to_from_engine.port)

        websocket_server.submit_result(
            to_from_engine.result_wrapper, address)


def run(engine_setup, engine_name):
    '''This should never return'''
    websocket_server = WebsocketServer()
    websocket_server.register_engine(engine_name)

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
