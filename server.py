import logging
from multiprocessing import Process
from client_comm import WebsocketServer


logger = logging.getLogger(__name__)


def _run_engine(self, engine_setup, input_queue, submit_result):
    engine = engine_setup()
    logger.info('Cognitive engine started')
    while True:
        input = input_queue.get()
        result = engine.handle(input)
        submit_result(result)


class Server:
    def __init__(self):
        self.websocket_server = WebsocketServer()

    def serve(self, engine_setup):
        process = Process(
            target=_run_engine,
            args=(engine_setup,
                  self.websocket_server.input_queue,
                  self.websocket_server.submit_result))
        process.start()
        self.websocket_server.launch()
