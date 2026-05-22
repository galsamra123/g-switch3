import logging
import pygame
from settings import *
logger = logging.getLogger(__name__)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, death_sprite, speed_sprites, win_sprite, map_height, my_id):
        super().__init__(group)
        self.image = pygame.image.load(f"graphics/player232.png").convert()  # loads player2 picture
        self.image.set_colorkey('white')
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        self.camera_x = 0
        self.limit_x = int(WINDOW_WIDTH * 0.75)
        self.min_x = int(WINDOW_WIDTH * 0.25)
        self.limit = False  # did the player reached the 3/4 of the screen
        self.map_height = map_height
        # rect
        self.rect = self.image.get_rect(topleft=pos)
        self.last_rect = self.rect.copy()

        # movement
        self.id = my_id
        if self.id == 1:
            self.gravity = 1

        else:
            self.gravity = -1

        self.y_changer = 10
        self.y_speed = 0
        self.x_changer = 5
        self.max_x = self.rect.x

        # collision
        self.collision_sprites = collision_sprites
        self.death_sprites = death_sprite
        self.speed_sprites = speed_sprites
        self.win_sprite = win_sprite
        self.is_dead = False
        self.won = False

    def on_wall(self):
        test_rect_y = self.last_rect.copy()
        test_rect_y.y += self.gravity  # checks 1 pixel in gravity direction

        for sprite in self.collision_sprites:
            if test_rect_y.colliderect(sprite.rect):  # if there is a collide with collision sprites (only walls)
                return True

        return False

    def flip_on_wall(self):
        if self.on_wall():
            self.gravity *= -1

    def flip_on_player(self):
        self.gravity *= -1

    def die(self):
        self.is_dead = True

    def win(self):
        self.won = True

    def move(self):
        # X movement + horizontal collision
        self.rect.x += self.x_changer
        limit_x = self.camera_x + self.limit_x
        min_x = self.camera_x + self.min_x
        if self.rect.right >= limit_x:
            self.limit = True
        if self.rect.left <= min_x:
            self.limit = False

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
                    # player hit the wall from the right -> put his left on wall right
                    logger.info('x.overlap')
                    if self.rect.left <= sprite.rect.right and self.last_rect.left >= sprite.last_rect.right:
                        self.rect.left = sprite.rect.right

                    # player hit the wall from the left -> put his right on wall left
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

        #for sprite in self.speed_sprites:
            #if self.limit and sprite.rect.colliderect(self.rect):
               # self.x_changer = 7

        for sprite in self.win_sprite:
            if sprite.rect.colliderect(self.rect):
                self.win()

    def collision_with_player(self, other):
        if self.is_dead or self.won:
            return

        if not self.rect.colliderect(other.rect):
            return

        if self.gravity == 1:
            # falling down: self on top of other
            if self.rect.bottom >= other.rect.top >= self.last_rect.bottom:
                self.rect.bottom = other.rect.top

        elif self.gravity == -1:
            # falling up: self under other
            if self.rect.top <= other.rect.bottom <= self.last_rect.top:
                self.rect.top = other.rect.bottom

    def update(self):
        if self.is_dead or self.won:
            return
        self.last_rect = self.rect.copy()
        self.move()
        if self.rect.x > self.max_x:
            self.max_x = self.rect.x
