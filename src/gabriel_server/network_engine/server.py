import asyncio
import time
import logging
import zmq
import zmq.asyncio
from types import SimpleNamespace
from gabriel_protocol import gabriel_pb2
from gabriel_server.websocket_server import WebsocketServer


ONE_MINUTE = 60


logger = logging.getLogger(__name__)


def run(websocket_port, zmq_address, num_tokens):
    context = zmq.asyncio.Context()
    zmq_socket = context.socket(zmq.ROUTER)
    zmq_socket.bind(zmq_address)

    server = _Server(websocket_port, num_tokens, zmq_socket)
    server.launch()


def _error_message(frame_id, status):
    result_wrapper = gabriel_pb2.ResultWrapper()
    result_wrapper.frame_id = frame_id
    result_wrapper.status = status

    return result_wrapper


class _Server(WebsocketServer):
    def __init__(self, websocket_port, num_tokens, zmq_socket, timeout):
        super().__init__(websocket_port, num_tokens)

        self._zmq_socket = zmq_socket
        self._engines = {}
        self._early_discard_filters = {}
        self._results_for_clients = asyncio.Queue()
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
            last_sent=0, current_frame=None)

        filter_info = self._early_discard_filters.get(filter_name)
        if filter_info is None:
            logger.info('An engine consumes inputs that passed filter %s',
                        filter_name)
            filter_info = SimpleNamespace(
                latest_input=None, outstanding_tokens=set(), engines=set())
            self._early_discard_filters[filter_name] = filter_info

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
        latest_input = filter_info.latest_input

        if result_wrapper.frame_id in filter_info.outstanding_tokens:
            await self._return_token(result_wrapper)

        if result_wrapper.frame_id < latest_input.frame_id:
            # send latest item to engine
            await self._send_helper(
                engine, latest_input.payload, latest_input.frame_id)
        else:
            # indicate engine is no longer busy
            engine.current_frame = None

    async def _return_token(self, result_wrapper):
        # FIXME _results_for_clients should have FromEngine instead of
        # ResultWrapper. Fix by storing host and port in engine and latest_input

        # Return token and results
        await self._results_for_clients.put(result_wrapper)

        filter_info.outstanding_tokens.remove(result_wrapper.frame_id)
        if latest_input.frame_id == result_wrapper.frame_id:
            latest_input.token_returned = True

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

            # Send heartbeat
            await self._zmq_socket.send_multipart([address, b'', b''])
            engine.last_sent = time.time()

    def _drop_engine(self, engine):
        filter_info = self._early_discard_filters[engine.filter_name]
        filter_info.engines.remove(engine)

        if engine.current_frame in filter_info.outstanding_tokens:
            # Return token
            frame_id = engine.current_frame
            status = gabriel_pb2.ResultWrapper.Status.ENGINE_ERROR
            result_wrapper = _engine_error_message(frame_id, status)
            self._return_token(result_wrapper)

        if len(filter_info.engines) == 0:
            logger.info('No remaining engines consume input from filter: %s',
                        engine.filter_name)
            del self._early_discard_filters[engine.filter_name]

        del self._engines[engine.address]

    async def _send_helper(self, engine, payload, frame_id):
        await self._zmq_socket.send_multipart([engine.address, b'', payload])
        engine.last_sent = time.time()
        engine.current_frame = frame_id

    async def _send_to_engine(self, to_engine):
        filter_passed = to_engine.from_client.filter_passed
        filter_info = self._early_discard_filters.get(filter_passed)

        if filter_info is None:
            # filter_passed will still be a key in self._free_engines even if
            # all engines that consume filter_passed are busy
            return ResultWrapper.Status.NO_ENGINE_FOR_FILTER_PASSED

        payload = to_engine.from_client.SerializeToString()
        frame_id = to_engine.from_client.frame_id
        for engine in filter_info.engines:
            if engine.current_frame is None:
                await send_helper(engine, payload, frame_id)

        if filter_info.lastest_input.frame_id not in outstanding_tokens:
            # No engines were given lastest_input
            # Return token for this input
            status = gabriel_pb2.ResultWrapper.Status.SERVER_DROPPED_FRAME
            result_wrapper = _engine_error_message(
                filter_info.lastest_input.frame_id, status)
            self._return_token(result_wrapper)

        frame_info.lastest_input = SimpleNamespace(
            frame_id=frame_id, payload=payload, token_returned=False)

    async def _recv_from_engine(self):
        return await self._results_for_clients.get()
