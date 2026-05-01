import pygame
import logging
from pytmx import load_pygame
from level import Level
from settings import *


class Game:
    def __init__(self):
        pygame.init()
        # Create the display surface
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('G-switch')

        self.tmx_maps = {0: load_pygame('graphics/map.tmx')}
        # Creating a dic that will contain all the level to swtich
        self.current_stage = Level(self.tmx_maps[0])

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

            self.current_stage.run()
            pygame.display.update()


if __name__ == '__main__':
    logging.basicConfig(
        filename="g_switch.log",
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    game = Game()
    game.run()
