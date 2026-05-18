import logging
import pygame
from settings import *

logger = logging.getLogger(__name__)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, death_sprite, win_sprite, map_width, map_height):
        super().__init__(groups)
        self.image = pygame.image.load(f"graphics/player1.png").convert()
        self.image.set_colorkey('white')
        self.map_width = map_width
        self.map_height = map_height
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        # rect
        self.rect = self.image.get_rect(topleft=pos)
        self.last_rect = self.rect.copy()

        # movement
        self.gravity = 1
        self.y_changer = 10
        self.y_speed = 0
        self.x_changer = 4

        # collision
        self.collision_sprites = collision_sprites
        self.death_sprites = death_sprite
        self.win_sprite = win_sprite
        self.is_dead = False
        self.won = False

    def on_ground_or_ceiling(self):
        test_rect_y = self.last_rect.copy()
        test_rect_y.y += self.gravity  # checks 1 pixel in gravity direction

        for sprite in self.collision_sprites:
            if test_rect_y.colliderect(sprite.rect):
                return True

        return False

    def flip(self):
        if self.on_ground_or_ceiling():
            self.gravity *= -1

    def die(self):
        self.is_dead = True

    def win(self):
        self.won = True

    def move(self):
        # X movement + horizontal collision
        self.rect.x += self.x_changer
        if self.rect.right >= self.map_width:
            self.rect.right = self.map_width - 32
        self.collision('horizontal')
        # Y movement + vertical collision
        self.y_speed = self.y_changer * self.gravity
        self.rect.y += self.y_speed
        if self.rect.bottom < 0 or self.rect.top > self.map_height:
            self.die()
        self.collision('vertical')

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):  # checks if the player collides with the wall sprites
                if axis == 'horizontal':  # (x axis)
                    # left
                    logger.info('x.overlap')
                    if self.rect.left <= sprite.rect.right and self.last_rect.left >= sprite.last_rect.right:
                        self.rect.left = sprite.rect.right

                    # right
                    if self.rect.right >= sprite.rect.left and self.last_rect.right <= sprite.last_rect.left:
                        self.rect.right = sprite.rect.left

                else:
                    # not horizontal than vertical (y axis)
                    logging.info('y overlap')

                    # moving down
                    if self.rect.bottom >= sprite.rect.top >= self.last_rect.bottom:
                        self.rect.bottom = sprite.rect.top

                    # moving up
                    if self.rect.top <= sprite.rect.bottom <= self.last_rect.top:
                        self.rect.top = sprite.rect.bottom

        for sprite in self.death_sprites:
            if sprite.rect.colliderect(self.rect):
                self.die()

        for sprite in self.win_sprite:
            if sprite.rect.colliderect(self.rect):
                self.win()

    def update(self):
        if self.is_dead or self.won:
            return
        self.last_rect = self.rect.copy()
        self.move()
