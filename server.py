import logging
from multiprocessing import Process, Pipe
from threading import Thread
from gabriel_server.client_comm import WebsocketServer
from gabriel_server import gabriel_pb2


logger = logging.getLogger(__name__)


def _run_engine(engine_setup, input_queue, conn):
    engine = engine_setup()
    logger.info('Cognitive engine started')
    while True:
        raw_input = input_queue.get()
        input = gabriel_pb2.Input()
        input.ParseFromString(raw_input)

        result = engine.handle(input)
        conn.send(result.SerializeToString())


def _queue_shuttle(websocket_server, conn):
    '''Add results to the output queue when they become available.

    We cannot add a coroutine to an event loop from a different process.
    Therefore, we need to run this in a different thread within the process
    running the event loop.'''

    while True:
        result = conn.recv()
        websocket_server.submit_result(result)


class Server:
    def __init__(self):
        self.websocket_server = WebsocketServer()

    def serve(self, engine_setup):
        '''This should never return'''

        parent_conn, child_conn = Pipe()
        shuttle_thread = Thread(
            target=_queue_shuttle,
            args=(self.websocket_server, parent_conn))
        shuttle_thread.start()
        engine_process = Process(
            target=_run_engine,
            args=(engine_setup, self.websocket_server.input_queue, child_conn))
        engine_process.start()

        self.websocket_server.launch()
