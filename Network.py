import socket
from protocol import *
from settings import *
import logging
logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, serverip):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # creates client_socket
        self.client_socket.settimeout(3)  # when connect() happens wait 3 seconds
        self.server = serverip
        self.port = SERVER_PORT
        self.addr = (self.server, self.port)  # tuple

        self.first_msg = self.connect()  # save the first msg cause it's the id

    def connect(self):
        try:
            self.client_socket.connect(self.addr)
            self.client_socket.settimeout(None)  # if connect succeed remove timeout
            logger.info(f"{self.client_socket} is Connected to server")
            return protocol_recive(self.client_socket)

        except (ConnectionError, socket.error, socket.timeout) as e:
            logger.error(f"{type(e).__name__}: {e}")
            self.client_socket.close()  # if after 3 seconds of error nothing happens stop
            raise ConnectionError("Connection error")

    def get_id(self):
        msg = self.first_msg
        if msg is None:
            logger.critical("msg is none")
            raise ConnectionError()

        msg = msg.decode()

        if msg.startswith('id,'):

            return int(msg.split(',')[1])
        raise ValueError(f"Expected id message, got: {msg}")

    def send(self, data):
        try:
            protocol_send(self.client_socket, data)

        except (ConnectionError, socket.error) as e:
            logger.error(f"{type(e).__name__}: {e}")
            return None

    def receive(self):
        try:
            return protocol_recive(self.client_socket)

        except (ConnectionError, socket.error) as e:
            logger.error(f"{type(e).__name__}: {e}")
            return None
