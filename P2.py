import pygame
from settings import *


class P2(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.is_dead = False
        self.won = False

    def update_pos(self, x, y):
        self.rect.topleft = (x, y)
