import struct

HEADER_SIZE = 4

# !I mean use big indian evan if the comp is in little as an
# unsigned int - positive int 4 byte long
# and py will make it work for all comp no matter of
# big or little indian is set in the operation


def protocol_send(sock, confirmation, data):
    """
    Send a response message back to the client.

    :param sock: Client socket to send data to.
    :param confirmation: Command result (success/fail).
    :param data: Payload data to send (bytes).
    :return: None
    """
    msg = confirmation.encode() + b',' + data
    final_length = struct.pack("!I", len(msg))
    final_msg = final_length + msg
    sock.sendall(final_msg)


def protocol_recive(sock):
    """
    Receive a message from the client and return (confirmation, data).

    :param sock: Client socket to read from.
    :return: Tuple of (confirmation: str, data: bytes)
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

    recive = 0
    recived = b""

    while recive < length_msg:
        byts = sock.recv(length_msg - recive)
        if byts == b'':
            raise ConnectionError
        recive += len(byts)
        recived += byts

    comma = recived.find(b',')
    confirmation = recived[:comma].decode()
    data = recived[comma + 1:]

    return confirmation, data
