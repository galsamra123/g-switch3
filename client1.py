import socket
from threading import Thread
from protocol import *


SERVER_IP = '127.0.0.1'
SERVER_PORT = 5001


def receive_msg(client_socket):
    while True:
        try:
            data = protocol_recive(client_socket)
            x, y = data.decode().split(",")
            x = int(x)
            y = int(y)
            print("other_player = ", "x= ", x, "y= ", y)

        except ValueError:
            print("invalid input: ", data.decode())

        except (ConnectionError, socket.error) as e:
            print(f"{type(e).__name__}: {e}")
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    full_msg = protocol_recive(client_socket)
    if full_msg[1].decode() == "server is full":
        print(full_msg[1].decode())
        print("bye")
        client_socket.close()
        return

    print("connected")

    recv_thread = Thread(
        target=receive_msg,
        args=(client_socket,),
        daemon=True
    )
    recv_thread.start()

    while True:
        msg = input("Enter message: ")

        if msg == "quit":
            break

        else:
            protocol_send(client_socket, "msg", msg.encode())


if __name__ == "__main__":
    main()
