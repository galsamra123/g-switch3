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


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        pygame.init()
        # Create the display surface
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('G-switch')

        self.tmx_maps = {0: load_pygame('graphics/maptest1.tmx')}
        # Creating a dic that will contain all the level to swtich
        self.current_stage = Level(self.tmx_maps[0])

        # server connection
        self.network = Connection()
        self.started = False

        Thread(
            target = self.receive_from_server,
            daemon = True
        ).start()

    def receive_from_server(self):
        while True:
            msg = self.network.receive()
            if msg is None:
                break
            if msg.decode() == "start":
                self.started = True
                continue
            msg = msg.decode()
            x, y, dead, won = msg.split(',')
            self.current_stage.p2.update_pos(int(x), int(y))
            self.current_stage.p2.is_dead = dead == 'True'
            self.current_stage.p2.won = won == 'True'

    def run(self):
        while True:
            # 1. Event Loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        logging.info('space pressed')
                        logging.info(self.current_stage.player.gravity)
                        self.current_stage.player.flip()
                        logging.info(self.current_stage.player.gravity)
            if self.started:
                self.current_stage.run()

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
