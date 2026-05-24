import pygame
from settings import *


class P2(pygame.sprite.Sprite):
    def __init__(self, pos, surf, group):
        super().__init__(group)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.last_rect = self.rect.copy()
        self.is_dead = False
        self.won = False

    def update_pos(self, x, y):
        self.last_rect = self.rect.copy()
        self.rect.topleft = (x, y)

