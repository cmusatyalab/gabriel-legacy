import logging
import asyncio
import multiprocessing
import queue
from gabriel_server import gabriel_pb2
import websockets


PORT = 9098


logger = logging.getLogger(__name__)
websockets_logger = logging.getLogger('websockets')

# The entire payload will be printed if this is allowed to be DEBUG
websockets_logger.setLevel(logging.INFO)


class WebsocketServer:
    def __init__(self, input_queue_maxsize=1):

        # multiprocessing.Queue is process safe
        self.input_queue = multiprocessing.Queue(input_queue_maxsize)

        # asyncio.Queue does not block the event loop
        self.result_queue = asyncio.Queue()

        self.event_loop = asyncio.get_event_loop()

    async def send_queue_full_message(self, websocket, frame_id):
        logger.warn('Queue full')
        output = gabriel_pb2.Output()
        output.status = gabriel_pb2.Output.Status.WRONG_INPUT_FORMAT
        await websocket.send(output.SerializeToString())

    async def consumer_handler(self, websocket):
        async for raw_input in websocket:
            logger.debug('Received input %s', websocket.local_address)
            try:
                # We cannot put the deserialized protobuf in a
                # multiprocessing.Queue because it cannot be pickled
                self.input_queue.put_nowait(raw_input)
            except queue.Full:
                input = gabriel_pb2.Input()
                input.ParseFromString(raw_input)
                await self.send_queue_full_message(websocket, input.frame_id)

    async def producer_handler(self, websocket):
        while True:
            output = await self.result_queue.get()
            logger.debug('Sending to %s', websocket.local_address)
            await websocket.send(output)

    async def handler(self, websocket, _):
        logger.info('New Client connected: %s', websocket.local_address)
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        logger.info('Client disconnected: %s', websocket.local_address)

    def launch(self):
        start_server = websockets.serve(self.handler, port=PORT)
        self.event_loop.run_until_complete(start_server)
        self.event_loop.run_forever()

    def submit_result(self, result):
        '''Add a result to self.result_queue.

        Can be called from a different process.'''

        asyncio.run_coroutine_threadsafe(
            self.result_queue.put(result), self.event_loop)
