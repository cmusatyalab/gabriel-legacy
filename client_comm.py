import logging
import asyncio
import multiprocessing
import gabriel_pb2
import websockets


PORT = 9098


logger = logging.getLogger(__name__)


class WebsocketServer:
    def __init__(self, input_queue_maxsize=1):

        # multiprocessing.Queue is process safe
        self.input_queue = multiprocessing.Queue(input_queue_maxsize)

        # asyncio.Queue does not block the event loop
        self.result_queue = asyncio.Queue()
        self.event_loop = asyncio.get_event_loop()

    async def send_queue_full_message(self, websocket, frame_id):
        logger.warn('Queue full')
        result = gabriel_pb2.Result()
        result.status = gabriel_pb2.Output.Status.QUEUE_FULL
        await websocket.send(result.SerializeToString())

    async def consumer_handler(self, websocket, path):
        async for raw_input in websocket:
            logger.debug('Received input from %s', path)
            input = gabriel_pb2.Input()
            input.ParseFromString(raw_input)
            try:
                self.input_queue.put_nowait(input)
            except multiprocessing.queue.Full:
                await self.send_queue_full_message(websocket, input.frame_id)

    async def producer_handler(self, websocket, path):
        while True:
            logger.debug('Sending to %s', path)
            result = await self.result_queue.get()
            await websocket.send(result.SerializeToString())

    async def handler(self, websocket, path):
        logger.info('New Client connected: %s', path)
        consumer_task = asyncio.ensure_future(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.ensure_future(
            self.producer_handler(websocket, path))
        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        logger.info('Client disconnected: %s', path)

    def launch(self):
        start_server = websockets.serve(self.handler, port=PORT)
        self.event_loop.run_until_complete(start_server)
        self.event_loop.run_forever()
        logger.debug('Event loop started')

    def submit_result(self, result):
        '''Add a result to self.result_queue.

        Can be called from a different process.'''

        asyncio.run_coroutine_threadsafe(
            self.result_queue.put(result), self.event_loop)
