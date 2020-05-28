import logging
import asyncio
import multiprocessing
import queue
from gabriel_protocol import gabriel_pb2
from gabriel_protocol.gabriel_pb2.ResultWrapper import Status
import websockets
from abc import ABC
from abc import abstractmethod
from collections import namedtuple


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
    def __init__(self, port, num_tokens_per_filter, message_max_size=None):
        self._port = port
        self._num_tokens_per_filter = num_tokens_per_filter
        self._message_max_size = message_max_size
        self._clients = {}
        self._filters_consumed = set()
        self._event_loop = asyncio.get_event_loop()

    @abstractmethod
    async def _handle_input(self, to_engine):
        pass

    async def _consumer_handler(self, websocket, client):
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

                if filter_passed not in filters_consumed:
                    logger.error('No engines consume frames from %s',
                                filter_passed)
                    await _send_error(websocket, to_engine.from_client,
                                      Status.NO_ENGINE_FOR_FILTER_PASSED)
                    continue

                if client.tokens_for_filter[filter_passed] < 1:
                    logger.error(
                        'Client %s sending output of filter %s without tokens',
                        websocket.remote_address, filter_passed)

                    await _send_error(websocket, to_engine.from_client,
                                      Status.NO_TOKENS)
                    continue

                client.tokens_for_filter[filter_passed] -= 1
                await self._handle_input(to_engine)
        except websockets.exceptions.ConnectionClosed:
            return  # stop the handler

    async def _handler(self, websocket, _):
        address = websocket.remote_address
        logger.info('New Client connected: %s', address)

        client = namedtuple(
            tokens_for_filter={filter_name: self._num_tokens_per_filter
                               for filter_name in self._filters_consumed},
            websocket=websocket)
        self._clients[address] = client

        # Send client welcome message
        to_client = gabriel_pb2.ToClient()
        to_client.welcome_message.filters_consumed = list(
            self._filters_consumed)
        to_client.welcome_message.num_tokens_per_filter = (
            self._num_tokens_per_filter)
        await websocket.send(to_client.SerializeToString())

        try:
            await self._consumer_handler(websocket, client)
        finally:
            del self._clients[address]
            logger.info('Client disconnected: %s', address)

    def launch(self):
        start_server = websockets.serve(
            self._handler, port=self._port, max_size=self._message_max_size)
        self._event_loop.run_until_complete(start_server)
        self._event_loop.run_forever()

    async def _send_result_helper(self, result_wrapper, address):
        client = self._clients.get(address)
        if client is None:
            logger.warning('Result for nonexistant address %s', address)
            return

        client.tokens_for_filter[result_wrapper.filter_passed] += 1

        to_client = gabriel_pb2.ToClient()
        to_client.result_wrapper.CopyFrom(result_wrapper)
        logger.debug('Sending to %s', address)
        await client.websocket.send(to_client.SerializeToString())

    def send_result(self, result_wrapper, address):
        '''Schedule event to send result to address.

        Can be called from a different thread. But this thread must be part of
        the same process as the thread that is running the event loop.'''

        asyncio.run_coroutine_threadsafe(
            self._send_result_helper(result_wrapper, address), self._event_loop)

    def add_filter_consumed(self, filter_name):
        '''Indicate that at least one cognitive engine consumes frames that
        pass filter_name.

        Must be called before self.launch() or run on self._event_loop.'''

        self._filters_consumed.add(filter_name)
        for client in clients:
            client.tokens_for_filter[filter_name] = self._num_tokens_per_filter

    def remove_filter_consumed(self, filter_name):
        '''Indicate that all cognitive engines that consumed frames that
        pass filter_name have been stopped.

        Must be called before self.launch() or run on self._event_loop.'''

        self._filters_consumed.remove(filter_name)
        for client in clients:
            del client.tokens_for_filter[filter_name]
