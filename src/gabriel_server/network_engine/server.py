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
        self._engine_workers = {}
        self._filter_infos = {}
        self._from_engines = asyncio.Queue()
        self._timeout = timeout
        self._size_for_queues = size_for_queues

    def launch(self):
        # We cannot use while self.is_running because these loops would
        # terminate before super().launch() is called launch
        async def receive_from_engine_worker_loop():
            while True:
                await self._receive_from_engine_worker_helper()

        async def heartbeat_loop():
            while True:
                await asyncio.sleep(self._timeout)
                await self._heartbeat_helper()

        asyncio.ensure_future(receive_from_engine_worker_loop())
        asyncio.ensure_future(heartbeat_loop())
        super().launch()

    async def _receive_from_engine_worker_helper(self):
        address, _, payload = await self._zmq_socket.recv_multipart()

        engine_worker = self._engine_workers.get(address)
        if engine_worker is None:
            await self._add_engine_worker(payload.decode(), address)
            return

        engine.record_payload_or_heatbeat()
        if payload == ''b:
            # Heartbeat response
            return

        result_wrapper = gabriel_pb2.ResultWrapper()
        result_wrapper.ParseFromString(payload)
        metadata = engine_worker.current_input_metadata
        filter_info = self._filter_infos[result_wrapper.filter_passed]

        assert result_wrapper.frame_id == metadata.frame_id
        await filter_info.respond_to_client(metadata, result_wrapper)

    async def _add_engine_worker(self, filter_name, address):
        logger.info('New engine connected that consumes filter: %s',
                    filter_name)

        filter_info = self._filter_infos.get(filter_name)
        if filter_info is None:
            logger.info('No existing engines accept input that passed filter: '
                        '%s', filter_name)
            filter_info = _FilterInfo(self._size_for_queues)
            self._filter_infos[filter_name] = filter_info

            # Tell super() to accept inputs that have passed filter_name
            self.add_filter_consumed(filter_name)

        engine_worker = _EngineWorker(self._zmq_socket, filter_info, address)
        self._engines_workers[address] = engine_worker

        filter_info.add_engine_worker(engine_worker)
        latest_input = filter_info.get_latest_input()
        if latest_input is None:
            filter_info.add_free_engine_worker(engine_worker)
        else:
            engine_worker.send_payload(
                latest_input.metadata, latest_input.payload)

    async def _heartbeat_helper(self):
        current_time = time.time()
        for address, engine_worker in self._engine_workers.items():
            if (current_time - engine.last_sent) < self._timeout:
                continue

            if not engine_worker.outstanding_payload_or_heatbeat():
                engine_worker.send_heartbeat()
                continue

            filter_info = engine_worker.get_filter_info()
            logger.info('Lost connection to engine worker that consumes items '
                        'from filter: %s', filter_info.get_name())
            engine_worker.drop()
            del self._engine_workers[engine_workers.get_address()]

            if filter_info.has_no_engine_workers():
                logger.info('No remaining engines consume input from filter: '
                            '%s', engine.filter_name)
                filter_name = filter_info.get_name()
                del self._early_discard_filters[filter_name]
                self.remove_filter_consumed(filter_name)

    async def _send_to_engine(self, to_engine):
        filter_passed = to_engine.from_client.filter_passed
        filter_info = self._early_discard_filters[filter_passed]

        return await filter_info.handle_new_to_engine(to_engine)

    async def _recv_from_engine(self):
        return await self._from_engines.get()


class _EngineWorker:
    def __init__(self, zmq_socket, filter_info, address):
        self._zmq_socket = socket
        self._filter_info = filter_info
        self._address = address
        self._last_sent = 0
        self._outstanding_payload_or_heartbeat = False
        self._current_input_metadata = None

    def get_address(self):
        return self._address

    def get_filter_info(self):
        return self._filter_info

    def record_payload_or_heatbeat(self):
        self._outstanding_payload_or_heartbeat = False

    def outstanding_payload_or_heatbeat(self):
        return self._outstanding_payload_or_heartbeat

    def send_heartbeat(self):
        self._outstanding_payload_or_heartbeat = True
        await self._zmq_socket.send_multipart([address, b'', b''])

    async def drop(self):
        if self._current_input_metadata is not None:
            # Return token for frame engine was in the middle of processing
            status = gabriel_pb2.ResultWrapper.Status.ENGINE_ERROR
            metadata = self._current_input_metadata
            result_wrapper = cognitive_engine.error_result_wrapper(
                metadata.frame_id, status)
            await self._filter_info.respond_to_client(metadata, result_wrapper)

        self._filter_info.remove_engine_worker(engine_worker)

    async def send_payload(self, metadata, payload):
        self._outstanding_payload_or_heartbeat = True
        await self._zmq_socket.send_multipart([self._address, b'', payload])
        self._last_sent = time.time()
        self._current_input_metadata = metadata

    async def send_next_message_or_mark_free(self):
        latest_input = self._filter_info.get_latest_input()
        if latest_input.metadata != self._current_input_metadata:
            await self.send_payload(latest_input.metadata, latest_input.payload)
            return

        to_engine = get_unsent_to_engine
        if to_engine is None:
            self._mark_free()
            return

        metadata, payload = self.prepare_to_engine(to_engine)
        await self.send_payload(metadata, payload)

    def _mark_free(self):
        self._current_input_metadata = None
        self._filter_info.add_free_engine_worker(self)


class _FilterInfo:
    def __init__(self, filter_name, fresh_inputs_queue_size, from_engines):
        self._filter_name = filter_name
        self._unsent_to_engines = asyncio.Queue(maxsize=fresh_inputs_queue_size)
        self._from_engines = from_engines
        self._latest_input = None

        # Checked when engine disconnects, to see if any other engines consume
        # items from this filter.
        self._engine_workers=set()

        # Checked in self.handle_new_to_engine() to see if we should send the
        # input to one or more engine handlers or add the input to
        # self._unsent_to_engines.
        self._free_engine_workers=set()

    def get_name():
        return self._filter_name

    def add_engine_worker(self, engine_worker):
        self._engine_workers.add(engine_worker)

    def add_free_engine_worker(self, engine_worker):
        self._free_engine_workers.add(engine_worker)

    def remove_engine_worker(self, engine_worker):
        self._engine_workers.remove(engine_worker)
        self._free_engine_workers.discard(engine_worker)

    def has_no_engine_workers(self):
        return len(self._engine_workers) > 0

    def get_latest_input(self):
        return self._latest_input

    async def handle_new_to_engine(self, to_engine):
        if len(self._free_engine_workers) == 0:
            if self._unsent_to_engines.full():
                return False

            self._unsent_to_engines.put_nowait(to_engine)
            return True

        (metadata, payload) = self.prepare_to_engine(to_engine)
        for engine_worker in self._free_engine_workers:
            await engine_worker.send_payload(metadata, payload)

        self._free_engine_workers.clear()

    async def respond_to_client(self, metadata, result_wrapper):
        if (self._latest_input.token_returned or
            self._latest_input.metadata != metadata)
            # We already responded to client for message corresponding to
            # metadata for this filter.
            return

        from_engine = cognitive_engine.pack_from_engine(
            metadata.host, metadata.port, result_wrapper)
        await self._from_engines.put(from_engine)

        self._latest_input.token_returned = True

    def get_unsent_to_engine(self):
        '''
        Return next unsent item from queue, or None if queue is empty.
        '''

        if self._fresh_inputs.empty():
            return None

        return self._unsent_to_engines.get_nowait()

    def prepare_to_engine(self, to_engine):
        '''Update internal state to reflect that to_engine is about to be sent,
        and return payload and metadata.'''
        metadata = Metadata(frame_id=to_engine.from_client.frame_id,
                            host=to_engine.host, port=to_engine.port)
        payload = to_engine.from_client.SerializeToString()

        self._latest_input = SimpleNamespace(
            metadata=metadata, payload=payload, token_returned=False)
        return (metadata, payload)
