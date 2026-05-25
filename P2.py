import pygame
import logging
logger = logging.getLogger(__name__)


class P2(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.draw_x = self.rect.x
        self.draw_y = self.rect.y
        self.last_rect = self.rect.copy()
        self.is_dead = False
        self.won = False

    def update_pos(self, x, y):
        self.last_rect = self.rect.copy()
        logger.info(f"last rect: {self.last_rect}")
        self.rect.topleft = (x, y)
        logger.info(f"update rect: {self.rect}")

    def smoth_draw(self):
        self.draw_x += (self.rect.x - self.draw_x) * 0.45
        logger.info(f"smoth draw x: {self.draw_x}")
        self.draw_y += (self.rect.y - self.draw_y) * 0.45
        logger.info(f"smoth draw y: {self.draw_y}")