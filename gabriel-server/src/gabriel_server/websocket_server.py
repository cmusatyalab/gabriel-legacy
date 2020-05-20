import logging
import asyncio
import multiprocessing
import queue
from gabriel_protocol import gabriel_pb2
from gabriel_protocol.gabriel_pb2.ResultWrapper import Status
import websockets
from abc import ABC
from abc import abstractmethod
from collections import defaultdict, namedtuple


logger = logging.getLogger(__name__)
websockets_logger = logging.getLogger(websockets.__name__)


# The entire payload will be printed if this is allowed to be DEBUG
websockets_logger.setLevel(logging.INFO)


async def _send_error(websocket, from_client, status):
    to_client = gabriel_pb2.ToClient()
    to_client.result_wrapper.frame_id = from_client.frame_id
    to_client.result_wrapper.status = status
    await websocket.send(to_client.SerializeToString())


class WebsocketServer(ABC):
    def __init__(self, port, num_tokens, message_max_size=None):

        self._port = port
        self._num_tokens_per_filter = num_tokens
        self._message_max_size = message_max_size
        self._clients = {}
        self._event_loop = asyncio.get_event_loop()

    @abstractmethod
    async def handle_input(self, to_engine_serialized):
        pass

    async def consumer_handler(self, websocket, client):
        address = websocket.remote_address

        try:
            # TODO: ADD this line back in once we can stop supporting Python 3.5
            # async for raw_input in websocket:

            # TODO: Remove the following two lines when we can stop supporting
            # Python 3.5
            while True:
                raw_input = await websocket.recv()

                logger.debug('Received input from %s', address)

                to_engine = gabriel_pb2.ToEngine()
                to_engine.host = address[0]
                to_engine.port = address[1]
                to_engine.from_client.ParseFromString(raw_input)

                filter_passed = to_engine.from_client.filter_passed

                if filter_passed not in client.tokens_for_filter:
                    logger.error('No engines consume frames from %s',
                                filter_passed)
                    await _send_error(websocket, to_engine.from_client,
                                      Status.REQUESTED_ENGINE_NOT_AVAILABLE)
                    continue

                if client.tokens_for_filter[filter_passed] < 1:
                    logger.error(
                        'Client %s sending output of filter %s without tokens',
                        websocket.remote_address, filter_passed)

                    await _send_error(websocket, to_engine.from_client,
                                      Status.NO_TOKENS)
                    continue

                # TODO give token back if engine rejects frame
                client.tokens_for_filter[filter_passed] -= 1
                await self.handle_input(to_engine.SerializeToString())
        except websockets.exceptions.ConnectionClosed:
            return  # stop the handler

    async def handler(self, websocket, _):
        address = websocket.remote_address
        logger.info('New Client connected: %s', address)

        # asyncio.Queue does not block the event loop
        result_queue = asyncio.Queue()

        client = namedtuple(
            tokens_for_filter=defaultdict(lambda: self._num_tokens_per_filter),
            websocket=websocket)
        self.clients[address] = client

        # Send client welcome message
        to_client = gabriel_pb2.ToClient()
        # TODO to_client.welcome_message.filters_consumed
        to_client.welcome_message.num_tokens_per_filter = (
            self._num_tokens_per_filter)
        await websocket.send(to_client.SerializeToString())

        try:
            await self.consumer_handler(websocket, client)
        finally:
            del self.clients[address]
            logger.info('Client disconnected: %s', address)

    def launch(self):
        start_server = websockets.serve(
            self.handler, port=self.port, max_size=self.message_max_size)
        self.event_loop.run_until_complete(start_server)
        self.event_loop.run_forever()

    async def _send_result_helper(self, result_wrapper, address, filter_name):
        client = self.clients.get(address)
        if client is None:
            logger.warning('Result for nonexistant address %s', address)
            return

        client.tokens_for_filter[filter_name] += 1

        to_client = gabriel_pb2.ToClient()
        to_client.result_wrapper.CopyFrom(result_wrapper)
        logger.debug('Sending to %s', address)
        await client.websocket.send(to_client.SerializeToString())

    def send_result(self, result_wrapper, address, filter_name):
        '''Schedule event to send result to address.

        Return token for filter_name for client.

        Can be called from a different thread. But this thread must be part of
        the same process as the event loop.'''

        asyncio.run_coroutine_threadsafe(
            self._send_result_helper(result_wrapper, address, filter_name),
            self.event_loop)

    def register_engine(self, engine_name):
        '''Add a cognitive engine to self._available_engines.

        Done on event loop because set() is not thread safe.'''

        self.event_loop.call_soon_threadsafe(
            self._available_engines.add, engine_name)

    def unregister_engine(self, engine_name):
        '''Remove a cognitive engine from self._available_engines.

        Done on event loop because set() is not thread safe.'''

        self.event_loop.call_soon_threadsafe(
            self._available_engines.remove, engine_name)
