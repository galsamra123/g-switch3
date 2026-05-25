import struct
import logging
logger = logging.getLogger(__name__)

HEADER_SIZE = 4

# !I mean use big indian evan if the comp is in little as an
# unsigned int - positive int 4 byte long
# and py will make it work for all comp no matter of
# big or little indian is set in the operation


def protocol_send(sock, data):
    """
    Send a response message back to the client.

    :param sock: Client socket to send data to.
    :param data: Payload data to send (bytes).
    :return: None
    """
    logger.debug(f"Sending {len(data)} bytes to {sock}")
    final_length = struct.pack("!I", len(data))
    sock.sendall(final_length+data)


def protocol_recive(sock):
    """
    Receive a message from the client and return (data).

    :param sock: Client socket to read from.
    :return:  data as bytes
    """
    recive = 0
    recived = b""

    while recive < HEADER_SIZE:
        byts = sock.recv(HEADER_SIZE - recive)
        if byts == b'':
            raise ConnectionError
        recive += len(byts)
        recived += byts

    length_msg = struct.unpack("!I", recived)[0]
    logger.info(f"Received {length_msg} bytes from {sock}")

    recive = 0
    recived = b""

    while recive < length_msg:
        byts = sock.recv(length_msg - recive)
        if byts == b'':
            raise ConnectionError
        recive += len(byts)
        recived += byts
    logger.info(f"Received {recived} bytes from {sock}")
    return recived
