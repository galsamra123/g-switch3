import pygame

from settings import *
import logging

logger = logging.getLogger(__name__)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites):
        super().__init__(groups)
        self.image = pygame.image.load(f"graphics/player2.png").convert()
        self.image.set_colorkey('white')
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        #rect
        self.rect = self.image.get_rect(topleft=pos)
        self.last_rect = self.rect.copy()

        # movement
        self.gravity = 1
        self.y_changer = 0.8
        self.y_speed = 0

        # collision
        self.collision_sprites = collision_sprites
        print(self.collision_sprites)

    def flip(self):
        self.gravity *= -1

    def move(self):
        self.y_speed = 2 * self.gravity
        self.rect.y += self.y_speed
        self.collision('vertical')

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):  # checks if the player collides with the wall sprites
                if axis == 'horizontal':  # (x axis)
                    # left
                    logging.info('x.overlap')
                    if self.rect.left <= sprite.rect.right and self.last_rect.left >= sprite.last_rect.right:
                        self.rect.left = sprite.rect.right

                    # right
                    if self.rect.right >= sprite.rect.left and self.last_rect.right >= sprite.last_rect.left:
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

    def update(self):
        self.last_rect = self.rect.copy()
        self.move()
