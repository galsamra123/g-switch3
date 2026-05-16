import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 8080


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect((SERVER_IP, SERVER_PORT))

    print("Connected to server")

    while True:
        msg = input("Enter message: ")

        if msg == "quit":
            break

        client_socket.send(msg.encode())

    client_socket.close()


if __name__ == "__main__":
    main()