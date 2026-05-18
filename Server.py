import sys
import socket
from threading import Thread
from protocol import *
from player import Player


QUEUE_SIZE = 4  # how many people can connect
IP = '0.0.0.0'
PORT = 5002
MAX_CLIENTS = 2
clients = []


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    try:
        print('New connection received from ' + client_address[0] + ':' + str(client_address[1]))

        while True:
            data = protocol_recive(client_socket)
            if not data:
                print("Client disconnected:", client_address)
                break
            if data.decode() == 'game over':
                print('game over')
                for client in clients:
                    protocol_send(client, 'game over'.encode())
            if data.decode() == 'again':
                print('again')
                for client in clients:
                    protocol_send(client, 'start'.encode())
            print(client_address, "sent:", data.decode())
            for client in clients:
                if client != client_socket:
                    protocol_send(client, data)

    except socket.error as err:
        print('received socket exception - ' + str(err))

    finally:
        if client_socket in clients:
            clients.remove(client_socket)
        client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)

        while True:
            client_socket, client_address = server_socket.accept()

            if len(clients) >= MAX_CLIENTS:
                print("server full")
                print("Client disconnected:", client_address)
                protocol_send(client_socket, "server is full".encode())
                client_socket.close()
                continue

            clients.append(client_socket)
            protocol_send(client_socket, "connected to server".encode())
            if len(clients) == MAX_CLIENTS:
                for client in clients:
                    protocol_send(client, "start".encode())
            print('Accepted connection from: ', client_address)
            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
