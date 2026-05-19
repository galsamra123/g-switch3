import pygame
import logging
import sys

from pytmx import load_pygame
from level import Level
from settings import *
import socket
from threading import Thread
from Network import Connection
from protocol import *
from datetime import datetime


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        pygame.init()
        # Create the display surface
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('G-switch')

        self.network = Connection()
        self.player_id = self.network.get_id()
        print(self.player_id)

        self.tmx_maps = {0: load_pygame('graphics/maptest1.tmx')}
        # Creating a dic that will contain all the level to switch
        self.current_stage = Level(self.tmx_maps[0], self.player_id)

        # server connection
        self.started = False
        self.game_over = False
        self.i_quit = False
        Thread(
            target=self.receive_from_server,
            daemon=True
        ).start()

    def receive_from_server(self):
        while True:
            msg = self.network.receive()
            if msg is None:
                break
            msg = msg.decode()

            if msg == "start":
                self.started = True
                continue
            if msg == 'game over':
                self.started = False
                self.game_over = True
                continue

            x, y, dead, won = msg.split(',')
            self.current_stage.p2.update_pos(int(x), int(y))
            self.current_stage.p2.is_dead = dead == 'True'  # comes as text so needed to turn to bool
            self.current_stage.p2.won = won == 'True'

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
                    if event.key == pygame.K_SPACE:
                        logging.info('space pressed')
                        logging.info(self.current_stage.player.gravity)
                        self.current_stage.player.flip()
                        logging.info(self.current_stage.player.gravity)
            if self.started or self.game_over:
                self.current_stage.run(self.game_over)

                p1_finished = self.current_stage.player.is_dead or self.current_stage.player.won
                p2_finished = self.current_stage.p2.is_dead or self.current_stage.p2.won

                # if game_over == false and both finished trigger happen once cause
                # right after game_over turns to ==true

                if not self.game_over and p1_finished and p2_finished:
                    self.network.send('game over'.encode())
                    self.game_over = True
                    self.started = False

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
