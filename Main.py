
import pygame
import logging
import sys

from pytmx import load_pygame
from level import Level
from settings import *
from threading import Thread
from Network import Connection


def input_serverip(screen, clock, num):
    title_font = pygame.font.Font(None, 75)
    title1_font = pygame.font.Font(None, 50)
    title2_font = pygame.font.Font(None, 32)
    title3_font = pygame.font.Font(None, 25)
    input_text = ""

    while True:
        screen.fill('black')
        title = title_font.render("WELCOME TO G-switch BY GAL HEICHAL SAMRA", True, "RED")
        title1 = title1_font.render("input the server IPv4", True, "white")
        title2 = title2_font.render(input_text, True, "white")
        title3 = title3_font.render("press ENTER to connect", True, "gray")
        new_title = title2_font.render("wrong ip try again", True, "red")

        screen.blit(title, (WINDOW_WIDTH / 2 - title.get_width() / 2, WINDOW_HEIGHT / 4))
        screen.blit(title1, (WINDOW_WIDTH / 2 - title1.get_width() / 2, WINDOW_HEIGHT / 2))
        pygame.draw.rect(screen, "white", pygame.Rect(WINDOW_WIDTH / 2 - 200, 250, 400, 60), 2)
        screen.blit(title2, (WINDOW_WIDTH / 2 - 190, 270))
        screen.blit(title3, (WINDOW_WIDTH / 2 - title3.get_width() / 2, 450))
        if num > 1:
            screen.blit(new_title, (WINDOW_WIDTH / 2 - new_title.get_width() / 2, 370))

        pygame.display.update()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # K_RETURN = ENTER
                    # screen.blit(title4, (WINDOW_WIDTH/2 - title4.get_width() / 2, WINDOW_HEIGHT - 100))
                    return input_text.strip()

                elif event.key == pygame.K_BACKSPACE:  # K_BACKSPACE = eraser
                    input_text = input_text[:-1]

                else:
                    input_text += event.unicode


def wait_for_others(screen):
    font = pygame.font.Font(None, 40)

    screen.fill("black")

    waiting_text = font.render(
        "great you submitted, waiting for other player...",
        True,
        "gray"
    )

    screen.blit(
        waiting_text,
        (WINDOW_WIDTH // 2 - waiting_text.get_width() // 2, 500)
    )

    pygame.display.update()


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        pygame.init()
        # Create the display surface
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('G-switch')

        self.ip_success = False
        self.num_of_ip = 1
        while not self.ip_success:
            server_ip = input_serverip(self.display_surface, self.clock, self.num_of_ip)

            try:
                self.network = Connection(server_ip)
                self.player_id = self.network.get_id()
                self.ip_success = True
                wait_for_others(self.display_surface)

            except ConnectionError as e:
                logging.error(f"error is: {e}")
                self.num_of_ip += 1

            except ValueError as e:
                logging.error(f"error is: {e}")

        self.tmx_maps = {0: load_pygame('graphics/maptest1.tmx')}
        # Creating a dic that will contain all the level to switch

        self.current_stage = Level(self.tmx_maps[0], self.player_id)
        # starts class Level in here Level == current_stage

        # server connection
        self.started = False
        self.game_over = False
        self.winner_id = None
        self.winner_txt = ""
        Thread(
            target=self.receive_from_server,
            daemon=True
        ).start()

    def winner_screen(self, winner, screen):
        title_font = pygame.font.Font(None, 100)
        title1_font = pygame.font.Font(None, 50)
        screen.fill("black")
        title = title_font.render(winner, True, "white")
        titel1 = title1_font.render("for restart press R", True, "gray")

        screen.blit(title, (WINDOW_WIDTH / 2 - title.get_width() / 2, WINDOW_HEIGHT / 2))
        screen.blit(titel1, (WINDOW_WIDTH / 2 - titel1.get_width() / 2,
                             WINDOW_HEIGHT / 2 - title.get_height() - 25))

    def receive_from_server(self):
        while True:
            msg = self.network.receive()
            if msg is None:
                break
            msg = msg.decode()

            if msg == "start":
                self.started = True
                continue

            if msg.startswith('result,'):
                string, winner_id, loser_id = msg.split(',')
                self.winner_id = int(winner_id)
                if self.winner_id == self.player_id:
                    winner = "YOU WIN"
                else:
                    winner = "YOU LOSE"
                self.started = False
                self.game_over = True
                self.winner_txt = winner
                continue
            x, y, dead, won = msg.split(',')
            self.current_stage.p2.update_pos(int(x), int(y))
            self.current_stage.p2.is_dead = dead == 'True'  # comes as text so needed to turn to bool
            self.current_stage.p2.won = won == 'True'

    def restart(self):
        try:
            self.network.client_socket.close()

        except OSError as e:
            print(f"socket already close: {e}")

        self.__init__()

    def run(self):
        while True:
            # 1. Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    player = self.current_stage.player
                    quit_msg = f"{player.rect.x},{player.rect.y},{True},{False}"
                    self.network.send(quit_msg.encode())
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.restart()

                    elif event.key == pygame.K_SPACE:
                        logging.info('space pressed')
                        logging.info(self.current_stage.player.gravity)
                        before_flip_gravity = self.current_stage.player.gravity
                        self.current_stage.player.flip_on_wall()
                        if self.current_stage.player.gravity == before_flip_gravity:  # if wall flip not happen
                            self.current_stage.flip_on_player()
                        logging.info(self.current_stage.player.gravity)
            if self.started or self.game_over:
                self.current_stage.run(self.game_over)

            if self.game_over:
                self.winner_screen(self.winner_txt, self.display_surface)

            if self.started:
                player = self.current_stage.player
                msg = f"{player.rect.x},{player.rect.y},{player.is_dead},{player.won}"
                self.network.send(msg.encode())

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    logging.basicConfig(
        filename="g_switch.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    game = Game()
    game.run()
