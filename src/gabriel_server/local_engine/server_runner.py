import asyncio
import fcntl
import logging
import os
import sys
import argparse
from gabriel_server.websocket_server import WebsocketServer
from gabriel_server.local_engine.common import write_message


# From https://www.golinuxhub.com/2018/05/how-to-view-and-increase-default-pipe-size-buffer.html
F_SETPIPE_SZ = 1031


def run(path_to_engine_runner, engine_name, port, num_tokens, pipe_size=None):
    '''pipe_size specifies the size (in bytes) of the pipe used to communicate
    between the Websocket server and the process running the cognitive engine.
    '''

    read, child_write = os.pipe2(0)
    cild_read, write = os.pipe2(os.O_NONBLOCK)

    if pipe_size is not None:
        fcntl.fcntl(fifo_fd, F_SETPIPE_SZ, child_write)
        fcntl.fcntl(fifo_fd, F_SETPIPE_SZ, write)

    server = WebsocketServer(port, num_tokens)
    server.register_engine(engine_name)

    asyncio.ensure_future(asyncio.create_subprocess_exec(
        sys.executable, path_to_engine_runner, str(child_write),
        str(child_read), close_fds=False))

    server.launch()
    raise Exception('Server stopped')
