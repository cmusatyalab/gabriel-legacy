import logging
import os
import argparse
from gabriel_protocol import gabriel_pb2
from gabriel_server.local_engine import common


logger = logging.getLogger(__name__)


def _receive_n_bytes(fd, n):
    # Based on https://docs.python.org/3.8/howto/sockets.html#using-a-socket
    chunks = []
    bytes_recd = 0
    while bytes_recd < n:
        chunk = os.read(fd, n - bytes_recd)
        assert chunk != b'', 'Pipe EOF reached'
        chunks.append(chunk)
        bytes_recd += len(chunk)
    return b''.join(chunks)


def _receive_message(fd):
    '''Read serialized protobuf message from file descriptor fd.

    The size of the bytestring is read. Then the bytestring itself is read.'''

    size_bytes = _receive_n_bytes(fd, common.NUM_BYTES_FOR_SIZE)
    size_of_message = int.from_bytes(size_bytes, byteorder=common.BYTEORDER)
    return _receive_n_bytes(fd, size_of_message)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('write', type=int)
    parser.add_argument('read', type=int)
    args = parser.parse_args()


def run(args, engine):
    while True:
        to_engine = gabriel_pb2.ToEngine()
        to_engine.ParseFromString(_receive_message(args.read))
        logger.info('Received input')

        result_wrapper = engine.handle(to_from_engine.from_client)

        from_engine = gabriel_pb2.FromEngine()
        from_engine.host = to_engine.host
        from_engine.port = to_engine.port
        from_engine.result_wrapper.CopyFrom(result_wrapper)

        common.write_message(args.write, from_engine.SerializeToString())
