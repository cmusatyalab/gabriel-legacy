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


def run(websocket_port, zmq_address, num_tokens):
    context = zmq.asyncio.Context()
    zmq_socket = context.socket(zmq.ROUTER)
    zmq_socket.bind(zmq_address)

    server = _Server(websocket_port, num_tokens, zmq_socket)
    server.launch()


class _Server(WebsocketServer):
    def __init__(self, websocket_port, num_tokens, zmq_socket, timeout):
        super().__init__(websocket_port, num_tokens)

        self._zmq_socket = zmq_socket
        self._engines = {}
        self._early_discard_filters = {}
        self._from_engines = asyncio.Queue()
        self._timeout = timeout

    def launch(self):
        # We cannot use while self.is_running because these loops would
        # terminate before super().launch() is called launch
        async def receive_from_engine_loop():
            while True:
                await self._receive_from_engine_helper()

        async def heartbeat_loop():
            while True:
                asyncio.sleep(self._timeout)
                self._heartbeat_helper()

        asyncio.ensure_future(receive_from_engine_loop())
        asyncio.ensure_future(heartbeat_loop())
        super().launch()

    def _add_engine(self, filter_name, address):
        logger.info('New engine connected')
        engine = SimpleNamespace(
            filter_name=filter_name, address=address, last_recv=time.time(),
            last_sent=0, current_input_metadata=None)

        filter_info = self._early_discard_filters.get(filter_name)
        if filter_info is None:
            logger.info('An engine consumes inputs that passed filter %s',
                        filter_name)
            filter_info = SimpleNamespace(
                latest_input=None, awaiting_response=set(), engines=set())
            self._early_discard_filters[filter_name] = filter_info

            self.add_filter_consumed(filter_name)

        self._engines[address] = engine
        filter_info.engines.add(engine)

    async def _receive_from_engine_helper(self):
        address, _, payload = await self._zmq_socket.recv_multipart()

        engine = self._engines.get(address)
        if engine is None:
            self._add_engine(payload.decode(), address)
            return

        engine.last_recv = time.time()
        if payload == ''b:
            # Heartbeat response
            return

        result_wrapper = gabriel_pb2.ResultWrapper()
        result_wrapper.ParseFromString(payload)
        filter_info = self._early_discard_filters[result_wrapper.filter_passed]

        assert result_wrapper.frame_id == engine.current_input_metadata.frame_id

        if engine.current_input_metadata in filter_info.awaiting_response:
            await self._send_result_wrapper(
                engine.current_input_metadata, result_wrapper)

            filter_info.awaiting_response.remove(engine.current_input_metadata)

            latest_input_frame_id = filter_info.latest_input.metadata.frame_id
            if latest_input_frame_id == result_wrapper.frame_id:
                filter_info.latest_input.token_returned = True

        if engine.current_input_metadata != filter_info.latest_input.metadata:
            # send latest item to engine
            await self._send_helper(
                engine, latest_input.payload, latest_input.metadata)
        else:
            # indicate engine is no longer busy
            engine.current_input_metadata = None

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

        if engine.current_input_metadata in filter_info.awaiting_response:
            # Return token
            status = gabriel_pb2.ResultWrapper.Status.ENGINE_ERROR
            result_wrapper = cognitive_engine.error_result_wrapper(
                frame_id, status)
            self._return_token(engine, filter_info, result_wrapper)

        if len(filter_info.engines) == 0:
            logger.info('No remaining engines consume input from filter: %s',
                        engine.filter_name)
            del self._early_discard_filters[engine.filter_name]
            self.remove_filter_consumed(engine.filter_name)

        del self._engines[engine.address]

    async def _send_to_engine(self, to_engine):
        filter_passed = to_engine.from_client.filter_passed
        filter_info = self._early_discard_filters[filter_passed]

        payload = to_engine.from_client.SerializeToString()
        metadata = Metadata(
            frame_id=to_engine.from_client.frame_id, host=to_engine.host,
            port=to_engine.port)
        for engine in filter_info.engines:
            if engine.current_frame is None:
                await _send_helper(engine, payload, metadata)

        latest_input = filter_info.lastest_input
        if (latest_input is not None and
            latest_input.metadata not in filter_info.awaiting_response):
            # No engines were given lastest_input
            # Return token for this input
            status = gabriel_pb2.ResultWrapper.Status.SERVER_DROPPED_FRAME
            result_wrapper = cognitive_engine.error_result_wrapper(
                lastest_input.metadata.frame_id, status)
            await self._send_result_wrapper(
                latest_input.metadata, result_wrapper)

        frame_info.lastest_input = SimpleNamespace(
            metadata=metadata, payload=payload, token_returned=False)

        return True

    async def _send_helper(self, engine, payload, metadata):
        await self._zmq_socket.send_multipart([engine.address, b'', payload])
        engine.last_sent = time.time()
        engine.current_input_metadata = metadata

    async def _recv_from_engine(self):
        return await self._results_for_clients.get()
