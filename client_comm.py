import logging
import asyncio
import multiprocessing
import gabriel_pb2


logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, input_queue_maxsize=1):

        # multiprocessing.Queue is process safe
        self.input_queue = multiprocessing.Queue(input_queue_maxsize)

        # asyncio.Queue does not block the event loop
        self.result_queue = asyncio.Queue()

    async def consumer_handler(self, websocket):
        async for raw_input in websocket:
            input = gabriel_pb2.Input()
            input.ParseFromString(raw_input)
            try:
                self.input_queue.put_nowait(input)
            except multiprocessing.queue.Full:
                self.send_queue_full_message(websocket, input.frame_id)

    async def producer_handler(self, websocket):
        while True:
            result = await self.result_queue.get()
            await websocket.send(result.SerializeToString())
