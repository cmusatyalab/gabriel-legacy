import os


NUM_BYTES_FOR_SIZE = 4
BYTEORDER = 'big'


def write_message(fd, serialized_message):
    '''Write serialized protobuf message to file descriptor fd.

    The size of the bytestring is written. Then the bytestring itself is
    written.'''

    size_of_message = len(serialized_message)
    size_bytes = size_of_message.to_bytes(NUM_BYTES_FOR_SIZE,
                                          byteorder=BYTEORDER)

    num_bytes_written = os.write(fd, size_bytes)
    assert num_bytes_written == NUM_BYTES_FOR_SIZE, 'Write incomplete'

    num_bytes_written = os.write(fd, serialized_message)
    assert num_bytes_written == size_of_message, 'Write incomplete'
