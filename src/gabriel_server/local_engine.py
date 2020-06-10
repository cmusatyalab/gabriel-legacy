import asyncio
import logging
import multiprocessing
import os
import queue
from gabriel_protocol import gabriel_pb2
from gabriel_server.websocket_server import WebsocketServer


_NUM_BYTES_FOR_SIZE = 4
_BYTEORDER = 'big'


logger = logging.getLogger(__name__)


def run(engine_factory, filter_name, input_queue_maxsize, port, num_tokens):
    try:
        input_queue = multiprocessing.Queue(input_queue_maxsize)
        read, write = os.pipe()

        local_server = _LocalServer(port, num_tokens, input_queue, read)
        local_server.add_filter_consumed(filter_name)

        engine_process = multiprocessing.Process(
            target=_run_engine, args=(engine_factory, input_queue, read, write))
        engine_process.start()
        os.close(write)

        local_server.launch()
    finally:
        local_server.cleanup()
        os.close(read)

    raise Exception('Server stopped')


class _LocalServer(WebsocketServer):
    def __init__(self, port, num_tokens_per_filter, input_queue, read):
        super().__init__(port, num_tokens_per_filter)
        self._input_queue = input_queue

        loop = asyncio.get_event_loop()
        self._stream_reader = asyncio.StreamReader(loop=loop)
        def protocol_factory():
            return asyncio.StreamReaderProtocol(self._stream_reader)
        pipe = os.fdopen(read, mode='r')
        self._transport, _ = loop.run_until_complete(
            loop.connect_read_pipe(protocol_factory, pipe))

    def cleanup(self):
        self._transport.close()

    async def _send_to_engine(self, to_engine):
        try:
            self._input_queue.put_nowait(to_engine.SerializeToString())
        except queue.Full:
            return ResultWrapper.Status.SERVER_DROPPED_FRAME

        return ResultWrapper.Status.SUCCESS

    async def _recv_from_engine(self):
        '''Read serialized protobuf message.

        The size of the bytestring is read. Then the bytestring itself is
        read.'''
        size_bytes = await self._stream_reader.readexactly(_NUM_BYTES_FOR_SIZE)
        size_of_message = int.from_bytes(size_bytes, _BYTEORDER)
        from_engine_serialized = await self._stream_reader.readexactly(
            size_of_message)

        from_engine = gabriel_pb2.FromEngine()
        from_engine.ParseFromString(from_engine_serialized)
        return from_engine



def _run_engine(engine_factory, input_queue, read, write):
    try:
        os.close(read)

        engine = engine_factory()
        logger.info('Cognitive engine started')
        while True:
            to_engine = gabriel_pb2.ToEngine()
            to_engine.ParseFromString(input_queue.get())

            result_wrapper = engine.handle(to_engine.from_client)

            from_engine = gabriel_pb2.FromEngine()
            from_engine.host = to_engine.host
            from_engine.port = to_engine.port
            from_engine.return_token = True
            from_engine.result_wrapper.CopyFrom(result_wrapper)

            _write_message(write, from_engine.SerializeToString())
    finally:
        os.close(write)


def _write_message(fd, serialized_message):
    '''Write serialized protobuf message to file descriptor fd.

    The size of the bytestring is written. Then the bytestring itself is
    written.'''

    size_of_message = len(serialized_message)
    size_bytes = size_of_message.to_bytes(_NUM_BYTES_FOR_SIZE, _BYTEORDER)

    num_bytes_written = os.write(fd, size_bytes)
    assert num_bytes_written == _NUM_BYTES_FOR_SIZE, 'Write incomplete'

    num_bytes_written = os.write(fd, serialized_message)
    assert num_bytes_written == size_of_message, 'Write incomplete'
