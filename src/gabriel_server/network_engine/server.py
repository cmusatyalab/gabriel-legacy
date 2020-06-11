import asyncio
import time
import logging
import zmq
import zmq.asyncio
from collections import namedtuple
from types import SimpleNamespace
from gabriel_protocol import gabriel_pb2
from gabriel_server import cognitive_engine
from gabriel_server.websocket_server import WebsocketServer


ONE_MINUTE = 60


logger = logging.getLogger(__name__)


Metadata = namedtuple('Metadata', ['frame_id', 'host', 'port'])


def run(websocket_port, zmq_address, num_tokens, input_queue_maxsize,
        timeout=ONE_MINUTE):
    context = zmq.asyncio.Context()
    zmq_socket = context.socket(zmq.ROUTER)
    zmq_socket.bind(zmq_address)

    server = _Server(websocket_port, num_tokens, zmq_socket, timeout,
                     input_queue_maxsize)
    server.launch()


class _Server(WebsocketServer):
    def __init__(self, websocket_port, num_tokens, zmq_socket, timeout,
                 size_for_queues):
        super().__init__(websocket_port, num_tokens)

        self._zmq_socket = zmq_socket
        self._engines = {}
        self._early_discard_filters = {}
        self._from_engines = asyncio.Queue()
        self._timeout = timeout
        self._size_for_queues = size_for_queues

    def launch(self):
        # We cannot use while self.is_running because these loops would
        # terminate before super().launch() is called launch
        async def receive_from_engine_server_loop():
            while True:
                await self._receive_from_engine_server_helper()

        async def heartbeat_loop():
            while True:
                asyncio.sleep(self._timeout)
                self._heartbeat_helper()

        asyncio.ensure_future(receive_from_engine_loop())
        asyncio.ensure_future(heartbeat_loop())
        super().launch()

    async def _receive_from_engine_server_helper(self):
        address, _, payload = await self._zmq_socket.recv_multipart()

        engine = self._engines.get(address)
        if engine is None:
            self._add_engine_server(payload.decode(), address)
            return

        engine.last_recv = time.time()
        if payload == ''b:
            # Heartbeat response
            return

        result_wrapper = gabriel_pb2.ResultWrapper()
        result_wrapper.ParseFromString(payload)
        metadata = engine.current_input_metadata
        filter_info = self._early_discard_filters[result_wrapper.filter_passed]

        assert result_wrapper.frame_id == metadata.frame_id

        if filter_info.awaiting_response_for(metadata):
            await self._send_result_wrapper(metadata, result_wrapper)
            filter_info.mark_response_received(engine.current_input_metadata)

        next_input = filter_info.get_next_input(metadata)
        if next_input is None:
            # indicate engine is no longer busy
            engine.current_input_metadata = None
            filter_info.add_free_engine(engine)

        await self._send_helper(engine, next_input.metadata, next_input.payload)

    def _add_engine_server(self, filter_name, address):
        logger.info('New engine connected that consumes filter: %s',
                    filter_name)

        filter_info = self._early_discard_filters.get(filter_name)
        if filter_info is None:
            logger.info('An engine consumes inputs that passed filter %s',
                        filter_name)
            filter_info = _FilterInfo(self._size_for_queues)
            self._early_discard_filters[filter_name] = filter_info

            # Tell super() to accept inputs that have passed filter_name
            self.add_filter_consumed(filter_name)

        engine = SimpleNamespace(
            filter_name=filter_name, address=address, last_recv=time.time(),
            last_sent=0, current_input_metadata=None)
        self._engines[address] = engine

        filter_info.add_engine(engine)
        latest_input = filter_info.get_latest_input()
        if latest_input is None:
            filter_info.add_free_engine(engine)
        else:
            await self._send_helper(
                engine, latest_input.payload, latest_input.metadata)

    async def _send_result_wrapper(self, metadata, result_wrapper):
        from_engine = cognitive_engine.pack_from_engine(
            metadata.host, metadata.port, result_wrapper)
        await self._from_engines.put(from_engine)

    async def _heartbeat_helper(self):
        current_time = time.time()
        for address, engine in self._engines.items():
            if current_time - engine.last_recv < self._timeout:
                continue

            if (engine.last_sent - engine.last_recv) > self._timeout:
                logger.info('Lost connection to engines that consumes items '
                            'from filter: %s', engine.filter_name)
                self._drop_engine(engine)
                continue

            if current_time - engine.last_sent > self._timeout:
                # Send heartbeat
                await self._zmq_socket.send_multipart([address, b'', b''])
                engine.last_sent = time.time()

    def _drop_engine(self, engine):
        filter_info = self._early_discard_filters[engine.filter_name]
        filter_info.engines.remove(engine)

        if filter_info.awaiting_response_for(engine.current_input_metadata):
            # Return token
            status = gabriel_pb2.ResultWrapper.Status.ENGINE_ERROR
            metadata = engine.current_input_metadata
            result_wrapper = cognitive_engine.error_result_wrapper(
                metadata.frame_id, status)
            self._send_result_wrapper(metadata, result_wrapper)

        filter_info.remove_engine(engine)
        if filter_info.has_no_engines():
            logger.info('No remaining engines consume input from filter: %s',
                        engine.filter_name)
            del self._early_discard_filters[engine.filter_name]
            self.remove_filter_consumed(engine.filter_name)

        del self._engines[engine.address]

    async def _send_to_engine(self, to_engine):
        filter_passed = to_engine.from_client.filter_passed
        filter_info = self._early_discard_filters[filter_passed]

        metadata = Metadata(frame_id=to_engine.from_client.frame_id,
                            host=to_engine.host, port=to_engine.port)
        payload = to_engine.from_client.SerializeToString()

        if filter_info.all_engines_busy():
            return filter_info.add_fresh_input(metadata, payload)

        for engine in filter_info.get_free_engines():
            await _send_helper(engine, metadata, payload)
        filter_info.clear_free_engines()

        filter_info.mark_sent_to_server(metadata, payload)
        return True

    async def _send_helper(self, engine, metadata, payload):
        await self._zmq_socket.send_multipart([engine.address, b'', payload])
        engine.last_sent = time.time()
        engine.current_input_metadata = metadata

    async def _recv_from_engine(self):
        return await self._results_for_clients.get()


class _FilterInfo:
    def __init__(self, fresh_inputs_queue_size):
        self._fresh_inputs = asyncio.Queue(maxsize=fresh_inputs_queue_size)
        self._latest_input = None
        self._awaiting_response = set()
        self._engines=set()
        self._free_engines=set()

    def add_engine(self, engine):
        self._engines.add(engine)

    def remove_engine(self, engine):
        self._engines.remove(engine)
        self._awaiting_response.discard(engine)

    def has_no_engines(self):
        return len(self._engines) > 0

    def get_latest_input(self):
        return self._latest_input

    def add_free_engine(self, engine):
        self._free_engines.add(engine)

    def clear_free_engines(self):
        self._free_engines.clear()

    def all_engines_busy(self):
        return len(self._free_engines) == 0

    def add_fresh_input(self, metadata, payload):
        if self._fresh_inputs.full():
            return False

        self._fresh_inputs.put_nowait(SimpleNamespace(
            metadata=metadata, payload=payload))
        return True

    def get_free_engines(self):
        return self._free_engines

    def mark_sent_to_server(self, metadata, payload):
        self._lastest_input = SimpleNamespace(
            metadata=metadata, payload=payload, token_returned=False)
        self._awaiting_response.add(metadata)

    def mark_response_received(self, metadata):
        if self._latest_input.metadata == metadata:
            self._latest_input.token_returned = True
        self._awaiting_response.remove(metadata)

    def awaiting_response_for(self, metadata):
        return metadata in self._awaiting_response

    def get_next_input(self, metadata):
        '''
        Return the next input that should be given to an engine that has just
        finished processing metadata.

        Return None if metadata represents the latest input, and there are no
        fresh inputs on the queue.

        Update latest input, if we remove something from the queue
        '''

        if metadata != self._latest_input.metadata:
            return self._latest_input

        if self._fresh_inputs.empty():
            return None

        fresh_input = self._fresh_inputs.get_nowait()
        self.mark_sent_to_server(fresh_input.metadata, fresh_input.payload)
        return fresh_input
