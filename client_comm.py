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


ProtoHost = namedtuple('ProtoHost', ['proto', 'host'])


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
        host = websocket.remote_address[0]

        async for raw_input in websocket:
            logger.debug('Received input from %s', host)
            try:
                # We cannot put the deserialized protobuf in a
                # multiprocessing.Queue because it cannot be pickled
                proto_host = ProtoHost(proto=raw_input, host=host)
                self.input_queue.put_nowait(proto_host)
            except queue.Full:
                from_client = gabriel_pb2.FromClient()
                from_client.ParseFromString(raw_input)
                await self.send_queue_full_message(
                    websocket, from_client.frame_id)

    async def producer_handler(self, websocket, result_queue):
        host = websocket.remote_address[0]

        while True:
            output = await result_queue.get()
            logger.debug('Sending to %s', host)
            await websocket.send(output)

    async def handler(self, websocket, _):
        host = websocket.remote_address[0]
        logger.info('New Client connected: %s', host)

        # asyncio.Queue does not block the event loop
        result_queue = asyncio.Queue()
        self.result_queues[host] = result_queue

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
            del self.result_queues[host]
        logger.info('Client disconnected: %s', host)

    def launch(self):
        start_server = websockets.serve(self.handler, port=PORT)
        self.event_loop.run_until_complete(start_server)
        self.event_loop.run_forever()

    def submit_result(self, result, host):
        '''Add a result to self.result_queue.

        Can be called from a different process.'''

        asyncio.run_coroutine_threadsafe(
            self.result_queues[host].put(result),
            self.event_loop)
