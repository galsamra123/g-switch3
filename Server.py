import socket
from threading import Thread
from protocol import *
import logging


QUEUE_SIZE = 4  # how many people can connect
IP = '0.0.0.0'
PORT = 5002
MAX_CLIENTS = 2
clients = []
client_ids = {}
players_finished = {}
game_over = False
match_started = False


def handle_connection(client_socket, client_address):
    """
    handle a connection
    :param client_socket: the connection socket
    :param client_address: the remote address
    :return: None
    """
    global game_over, match_started

    try:
        logging.info('New connection received from ' + client_address[0] + ':' + str(client_address[1]))

        while True:
            data = protocol_recive(client_socket)  # recive b"x,y,dead,won"
            if not data:
                logging.info(f"Client disconnected: {client_address}")
                break
            msg = data.decode()

            try:
                x, y, dead, won = msg.split(',')
            except ValueError as e:
                logging.error(f"error: {e}")
                continue

            player_id = client_ids[client_socket]  # get from the dir the player id

            if not game_over and player_id not in players_finished:
                # if game not over check if the player finished already(dad/won)
                if dead == "True":
                    players_finished[player_id] = 'dead'
                    logging.info(f"player: {player_id} died")
                    logging.info(f"players_finished: {players_finished}")
                elif won == "True":
                    players_finished[player_id] = 'won'
                    logging.info(f"PLAYER {player_id} WON")
                    logging.info(f"players_finished: {players_finished}")

            for client in clients:
                if client != client_socket:
                    protocol_send(client, data)  # data = the recive from the start

            if not game_over and len(players_finished) == 2:
                p1_result = players_finished.get(1)
                p2_result = players_finished.get(2)

                if p1_result == 'won' and p2_result == 'dead':
                    winner_id = 1
                    loser_id = 2
                elif p1_result == 'dead' and p2_result == 'won':
                    winner_id = 2
                    loser_id = 1
                else:  # both win take first finisher or both lose take last finisher
                    finishers = list(players_finished.keys())  # puts the keys of the dic into a list by order
                    first = finishers[0]
                    second = finishers[1]

                    if p1_result == 'won' and p2_result == 'won':
                        winner_id = first
                        loser_id = second
                    else:  # both died
                        winner_id = second
                        loser_id = first

                game_over = True
                score_msg = f"result,{winner_id},{loser_id}"
                logging.info(f"GAME OVER RESULT: {score_msg}")
                for client in clients:
                    protocol_send(client, score_msg.encode())

            logging.info(f"{client_address} sent: {data.decode()}")

    except (socket.error, ConnectionError)as err:
        logging.error('received socket exception - ' + str(err))

    finally:
        disconnected_id = client_ids.get(client_socket)
        if client_socket in clients:
            clients.remove(client_socket)  # remove this socket from the clients list
        if client_socket in client_ids:
            del client_ids[client_socket]
            logging.info("CLIENT DISCONNECTED")
            logging.info(f"clients left: {len(clients)}")
            logging.info(f"match_started: {match_started} game_over: {game_over}")
            # remove client socket from the id dir
        if len(clients) == 0:
            logging.info("SERVER RESET - READY FOR NEW MATCH")
            match_started = False
            game_over = False
            players_finished.clear()
        if disconnected_id is not None and len(clients) > 0:
            loser_id = disconnected_id
            if loser_id == 1:
                winner_id = 2
            else:
                winner_id = 1
            game_over = True
            disconnect_msg = "0,0,True,False"
            score_msg = f"disconnect,{winner_id},{loser_id}"
            for client in clients:
                protocol_send(client, disconnect_msg.encode())
                protocol_send(client, score_msg.encode())
        client_socket.close()


def main():
    global match_started
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        logging.info("Listening for connections on port %d" % PORT)

        while True:
            client_socket, client_address = server_socket.accept()
            logging.info("new connect try")
            logging.info(f"clients: {len(clients)} matches started: {match_started} game over: {game_over}")

            if len(clients) >= MAX_CLIENTS or match_started:
                logging.info("server full")
                logging.info(f"Client disconnected: {client_address}")
                protocol_send(client_socket, "server is full".encode())
                client_socket.close()
                continue

            clients.append(client_socket)
            player_id = len(clients)
            client_ids[client_socket] = player_id  # adds to the dir client socket: id
            logging.info(f"{client_address} Player id: {player_id}")
            protocol_send(client_socket, f"id,{player_id}".encode())
            if len(clients) == MAX_CLIENTS:
                logging.info("match started")
                for client in clients:
                    protocol_send(client, "start".encode())
                    match_started = True
            logging.info(f'Accepted connection from: {client_address}')
            thread = Thread(target=handle_connection,
                            args=(client_socket, client_address))
            thread.start()
    except socket.error as err:
        logging.error('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    logging.basicConfig(
        filename="server.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main()
