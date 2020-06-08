import logging
import asyncio
import multiprocessing
import queue
from gabriel_protocol import gabriel_pb2
from gabriel_protocol.gabriel_pb2 import ResultWrapper
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
    to_client.return_token = True
    await websocket.send(to_client.SerializeToString())


_Client = namedtuple('_Client', ['tokens_for_filter', 'websocket'])


class WebsocketServer(ABC):
    def __init__(self, port, num_tokens_per_filter, message_max_size=None):
        self._port = port
        self._num_tokens_per_filter = num_tokens_per_filter
        self._message_max_size = message_max_size
        self._clients = {}
        self._filters_consumed = set()
        self._event_loop = asyncio.get_event_loop()

    @abstractmethod
    async def _send_to_engine(self, to_engine):
        '''Send ToEngine to the appropriate engine(s).

        Return True if send succeeded.'''
        pass

    @abstractmethod
    async def _recv_from_engine(self):
        '''Return serialized FromEngine message that the engine outputs.'''
        pass

    async def _handler(self, websocket, _):
        address = websocket.remote_address
        logger.info('New Client connected: %s', address)

        client = _Client(
            tokens_for_filter={filter_name: self._num_tokens_per_filter
                               for filter_name in self._filters_consumed},
            websocket=websocket)
        self._clients[address] = client

        # Send client welcome message
        to_client = gabriel_pb2.ToClient()
        for filter_name in self._filters_consumed:
            to_client.welcome_message.filters_consumed.append(filter_name)
        to_client.welcome_message.num_tokens_per_filter = (
            self._num_tokens_per_filter)
        to_client.return_token = False
        await websocket.send(to_client.SerializeToString())

        try:
            await self._consumer(websocket, client)
        finally:
            del self._clients[address]
            logger.info('Client disconnected: %s', address)

    async def _consumer(self, websocket, client):
        address = websocket.remote_address

        try:
            # TODO: ADD this line back in once we can stop supporting Python 3.5
            # async for raw_input in websocket:

            # TODO: Remove the following two lines when we can stop supporting
            # Python 3.5
            while websocket.open:
                raw_input = await websocket.recv()

                logger.debug('Received input from %s', address)

                to_engine = gabriel_pb2.ToEngine()
                to_engine.host = address[0]
                to_engine.port = address[1]
                to_engine.from_client.ParseFromString(raw_input)

                filter_passed = to_engine.from_client.filter_passed

                if filter_passed not in self._filters_consumed:
                    logger.error('No engines consume frames from %s',
                                filter_passed)
                    status = ResultWrapper.Status.NO_ENGINE_FOR_FILTER_PASSED
                    await _send_error(websocket, to_engine.from_client, status)
                    continue

                if client.tokens_for_filter[filter_passed] < 1:
                    logger.error(
                        'Client %s sending output of filter %s without tokens',
                        websocket.remote_address, filter_passed)

                    await _send_error(websocket, to_engine.from_client,
                                      ResultWrapper.Status.NO_TOKENS)
                    continue

                send_succeeded = await self._send_to_engine(to_engine)
                if not send_succeeded:
                    logger.error('Send to engine(s) that consume %s failed',
                                filter_passed)
                    await _send_error(websocket, to_engine.from_client,
                                      ResultWrapper.Status.SERVER_DROPPED_FRAME)
                    continue

                client.tokens_for_filter[filter_passed] -= 1
        except websockets.exceptions.ConnectionClosed:
            return  # stop the handler

    async def _producer(self, server):
        while server.is_serving():
            from_engine_serialized = await self._recv_from_engine()
            from_engine = gabriel_pb2.FromEngine()
            from_engine.ParseFromString(from_engine_serialized)
            address = (from_engine.host, from_engine.port)

            client = self._clients.get(address)
            if client is None:
                logger.warning('Result for nonexistant address %s', address)
                continue

            result_wrapper = from_engine.result_wrapper
            if from_engine.return_token:
                client.tokens_for_filter[result_wrapper.filter_passed] += 1

            to_client = gabriel_pb2.ToClient()
            to_client.result_wrapper.CopyFrom(result_wrapper)
            to_client.return_token = from_engine.return_token
            logger.debug('Sending to %s', address)
            try:
                await client.websocket.send(to_client.SerializeToString())
            except websockets.exceptions.ConnectionClosed:
                logger.info('Skipping message to %s', address)

    def launch(self):
        start_server = websockets.serve(
            self._handler, port=self._port, max_size=self._message_max_size)
        server = self._event_loop.run_until_complete(start_server)
        asyncio.ensure_future(self._producer(server))
        self._event_loop.run_forever()

    def add_filter_consumed(self, filter_name):
        '''Indicate that at least one cognitive engine consumes frames that
        pass filter_name.

        Must be called before self.launch() or run on self._event_loop.'''

        if filter_name in self._filters_consumed:
            return

        self._filters_consumed.add(filter_name)
        for client in self._clients:
            client.tokens_for_filter[filter_name] = self._num_tokens_per_filter

    def remove_filter_consumed(self, filter_name):
        '''Indicate that all cognitive engines that consumed frames that
        pass filter_name have been stopped.

        Must be called before self.launch() or run on self._event_loop.'''

        if filter_name not in self._filters_consumed:
            return

        self._filters_consumed.remove(filter_name)
        for client in clients:
            del client.tokens_for_filter[filter_name]
