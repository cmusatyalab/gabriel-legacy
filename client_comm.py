import logging
import asyncio
import multiprocessing
import queue
from gabriel_server import gabriel_pb2
import websockets
from collections import namedtuple


PORT = 9098


logger = logging.getLogger(__name__)
websockets_logger = logging.getLogger('websockets')

# The entire payload will be printed if this is allowed to be DEBUG
websockets_logger.setLevel(logging.INFO)


ProtoAddress = namedtuple('ProtoAddress', ['proto', 'address'])


class WebsocketServer:
    def __init__(self, input_queue_maxsize=1):

        # multiprocessing.Queue is process safe
        self.input_queue = multiprocessing.Queue(input_queue_maxsize)

        self.result_queues = {}

        self.event_loop = asyncio.get_event_loop()

    async def send_queue_full_message(self, websocket, frame_id):
        logger.warn('Queue full')
        from_server = gabriel_pb2.FromServer()
        from_server.frame_id = frame_id
        from_server.status = gabriel_pb2.FromServer.Status.QUEUE_FULL
        await websocket.send(from_server.SerializeToString())

    async def consumer_handler(self, websocket):
        address = websocket.remote_address

        async for raw_input in websocket:
            logger.debug('Received input from %s', address)
            try:
                # We cannot put the deserialized protobuf in a
                # multiprocessing.Queue because it cannot be pickled
                proto_address = ProtoAddress(proto=raw_input, address=address)
                self.input_queue.put_nowait(proto_address)
            except queue.Full:
                from_client = gabriel_pb2.FromClient()
                from_client.ParseFromString(raw_input)
                await self.send_queue_full_message(
                    websocket, from_client.frame_id)

    async def producer_handler(self, websocket, result_queue):
        address = websocket.remote_address

        while True:
            output = await result_queue.get()
            logger.debug('Sending to %s', address)
            await websocket.send(output)

    async def handler(self, websocket, _):
        address = websocket.remote_address
        logger.info('New Client connected: %s', address)

        # asyncio.Queue does not block the event loop
        result_queue = asyncio.Queue()
        self.result_queues[address] = result_queue

        try:
            consumer_task = asyncio.ensure_future(
                self.consumer_handler(websocket))
            producer_task = asyncio.ensure_future(
                self.producer_handler(websocket, result_queue))
            done, pending = await asyncio.wait(
                [consumer_task, producer_task],
                return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
        finally:
            del self.result_queues[address]
            logger.info('Client disconnected: %s', address)

    def launch(self):
        start_server = websockets.serve(self.handler, port=PORT)
        self.event_loop.run_until_complete(start_server)
        self.event_loop.run_forever()

    async def queue_result(self, result, address):
        result_queue = self.result_queues.get(address)
        if result_queue is None:
            logger.warning('Result for nonexistant address %s', address)
        else:
            await result_queue.put(result)

    def submit_result(self, result, address):
        '''Add a result to self.result_queue.

        Can be called from a different thread. But this thread must be part of
        the same process as the event loop.'''

        asyncio.run_coroutine_threadsafe(
            self.queue_result(result, address),
            self.event_loop)
