import socket
from protocol import *


class Connection:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '127.0.0.1'
        self.port = 5002
        self.addr = (self.server, self.port)

        self.first_msg = self.connect()

    def connect(self):
        try:
            self.client_socket.connect(self.addr)
            return protocol_recive(self.client_socket)
        except (ConnectionError, socket.error) as e:
            print(f"{type(e).__name__}: {e}")
            return None

    def get_id(self):
        msg = self.first_msg
        if msg is None:
            raise ConnectionError("No message")
        msg = msg.decode()

        if msg.startswith('id,'):

            return int(msg.split(',')[1])

        raise ValueError(f"Expected id message, got: {msg}")

    def send(self, data):
        try:
            protocol_send(self.client_socket, data)

        except (ConnectionError, socket.error) as e:
            print(f"{type(e).__name__}: {e}")
            return None

    def receive(self):
        try:
            return protocol_recive(self.client_socket)

        except (ConnectionError, socket.error) as e:
            print(f"{type(e).__name__}: {e}")
            return None
