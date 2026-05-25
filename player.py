import pygame
from settings import *
import logging

logger = logging.getLogger(__name__)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, death_sprite, win_sprite, map_height, my_id):
        super().__init__(group)
        self.image = pygame.image.load(f"graphics/player232.png").convert()  # loads player2 picture
        self.image.set_colorkey('white')
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        self.camera_x = 0
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

        # collision
        self.collision_sprites = collision_sprites
        self.death_sprites = death_sprite
        self.win_sprite = win_sprite
        self.is_dead = False
        self.won = False
        self.on_player = False

    def on_wall(self):
        test_rect_y = self.last_rect.copy()
        test_rect_y.y += self.gravity  # checks 1 pixel in gravity direction
        logger.info(f"test_rect_y: {test_rect_y}")

        for sprite in self.collision_sprites:
            if test_rect_y.colliderect(sprite.rect):  # if there is a collide with collision sprites (only walls)
                logger.info(f"im on wall sprite")
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
        logger.info(f"before move: {self.rect.x}, {self.rect.y}, {self.y_changer}")
        self.rect.x += self.x_changer
        logger.info(f"after move {self.rect.x}, {self.rect.y}, {self.y_changer}")

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
                    logger.info(f"check horizontal collision: {self.rect.x}, {self.rect.y},"
                                f" {self.last_rect.x}, {self.last_rect.y}")
                    if self.rect.left <= sprite.rect.right and self.last_rect.left >= sprite.last_rect.right:
                        self.rect.left = sprite.rect.right
                        logger.info(f"put my left on wall right")

                    # player hit the wall from the left -> put his right on wall left
                    if self.rect.right >= sprite.rect.left and self.last_rect.right <= sprite.last_rect.left:
                        self.rect.right = sprite.rect.left
                        logger.info(f"put my right on wall left")
                    logger.info(f"{self.rect.x}, {self.rect.y},"
                                f" {self.last_rect.x}, {self.last_rect.y}")

                else:
                    # not horizontal than vertical (y axis)
                    logger.info(f"check vertical collision: {self.rect.x}, {self.rect.y},"
                                f" {self.last_rect.x}, {self.last_rect.y}")

                    # moving down
                    if self.rect.bottom >= sprite.rect.top >= self.last_rect.bottom:
                        self.rect.bottom = sprite.rect.top
                        logger.info(f"put my bottom on wall top")

                    # moving up
                    if self.rect.top <= sprite.rect.bottom <= self.last_rect.top:
                        self.rect.top = sprite.rect.bottom
                        logger.info(f"put my top on wall bottom")
                    logger.info(f"{self.rect.x}, {self.rect.y},"
                                f" {self.last_rect.x}, {self.last_rect.y}")

        for sprite in self.death_sprites:
            if sprite.rect.colliderect(self.rect):
                logger.info(f"im on death sprite")
                self.die()

        for sprite in self.win_sprite:
            if sprite.rect.colliderect(self.rect):
                logger.info(f"won")
                self.win()

    def collision_with_player(self, other):
        self.on_player = False

        if self.is_dead or self.won:
            return False

        if other.is_dead or other.won:
            return False

        other_platform = other.rect.inflate(80, 0)  # make p2 hitbox 20 px larger on x
        logger.info(f"other_platform: {other_platform}")
        horizontal_overlap = (self.rect.right > other_platform.left and self.rect.left < other_platform.right)

        if not horizontal_overlap:
            return False

        margin = abs(self.y_speed) + 12  # player can jump more px and then the bottom/top won't be exactly the same
        # the abs for when gravity is -1 and then y speed < 0

        if self.gravity == 1:
            # gravity pulls player down:
            # if last frame player was above p2, and now player crossed/touched p2's top,
            # place player on top of p2 like he is a floor
            crossed_top = (
                    self.last_rect.bottom <= other_platform.top + margin  # player last bottom <= p2top + player px jump
                    and self.rect.bottom >= other_platform.top  # player bottom reached or passed p2 top
            )

            if crossed_top:
                self.rect.bottom = other_platform.top  # put them together
                logger.info(f"put my bottom on p2 top")
                self.y_speed = 0  # stop player fall
                self.on_player = True
                return True

        elif self.gravity == -1:
            # gravity pulls player up:
            # if last frame player was under p2, and now player crossed/touched p2's bottom,
            # place player under p2 like he is a ceiling/floor above player
            crossed_bottom = (
                    self.last_rect.top >= other_platform.bottom - margin  # player last top below or close to
                    # p2 bottom
                    and self.rect.top <= other_platform.bottom  # did player top reached / passed p2 bottom
            )

            if crossed_bottom:
                self.rect.top = other_platform.bottom
                logger.info(f"put my top on p2 bottom")
                self.y_speed = 0
                self.on_player = True
                return True

        return False

    def update(self):
        if self.is_dead or self.won:
            logger.info(f"is dead: {self.is_dead}, won: {self.won}")
            return
        self.last_rect = self.rect.copy()
        logger.info(f"last_rect: {self.last_rect}")
        self.move()
