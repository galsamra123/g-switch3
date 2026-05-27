from settings import *
import pygame
from sprites import Sprite
from player import Player
from P2 import P2
import logging
logger = logging.getLogger(__name__)


class Level:
    def __init__(self, tmx_map, player_id):

        self.window = pygame.display.get_surface()
        if self.window is None:
            raise ValueError("window was not initialized")
        self.all_sprites = pygame.sprite.Group()
        # creates List<Sprite> allSprites = new List<Sprite>();
        self.collisions_sprites = pygame.sprite.Group()
        self.death_sprites = pygame.sprite.Group()
        self.win_sprites = pygame.sprite.Group()
        self.player_id = player_id
        self.camera_x = 0
        self.camera_xchanger = 3

        # in setup
        self.p2 = None
        self.player = None
        self.bg = None
        self.map_height = None
        self.map_width = None

        self.setup(tmx_map)

    def setup(self, tmx_map):
        logging.info("LAYERS:")
        for layer in tmx_map.layers:
            logger.info(f"{layer.name} {type(layer)}")  # to see al the layer types in the map
        self.map_width = tmx_map.width * TILE_SIZE
        self.map_height = tmx_map.height * TILE_SIZE
        self.bg = tmx_map.get_layer_by_name('background').image

        for x, y, surf in tmx_map.get_layer_by_name('wall').tiles():  # print the walls to screen
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collisions_sprites))

        for x, y, surf in tmx_map.get_layer_by_name('death').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.death_sprites))

        for obj in tmx_map.get_layer_by_name('win'):
            Sprite((obj.x, obj.y), pygame.image.load('graphics/setpics/winflag.png').convert_alpha(),
                   (self.all_sprites, self.win_sprites))

        p2_surf = pygame.image.load("graphics/player132.png").convert()
        p2_surf.set_colorkey("white")
        p2_surf = pygame.transform.scale(p2_surf, (TILE_SIZE, TILE_SIZE))

        if self.player_id == 1:

            for obj in tmx_map.get_layer_by_name('player1'):
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collisions_sprites, self.death_sprites,
                                     self.win_sprites, self.map_height, self.player_id)
                logger.info(f"x: {obj.x} y: {obj.y}")

            for obj in tmx_map.get_layer_by_name('player2'):
                self.p2 = P2((obj.x, obj.y), p2_surf, self.all_sprites)
                logger.info(f"x: {obj.x} y: {obj.y}")

        else:
            for obj in tmx_map.get_layer_by_name('player2'):
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collisions_sprites, self.death_sprites,
                                     self.win_sprites, self.map_height, self.player_id)
                logger.info(f"x: {obj.x} y: {obj.y}")

            for obj in tmx_map.get_layer_by_name('player1'):
                self.p2 = P2((obj.x, obj.y), p2_surf, self.all_sprites)
                logger.info(f"x: {obj.x} y: {obj.y}")

    def flip_on_player(self):
        if self.player.is_dead or self.player.won:
            return

        if self.p2.is_dead or self.p2.won:
            return

        if self.player.on_player:
            self.player.flip_on_player()

    def run(self, match_over):
        self.player.camera_x = self.camera_x  # changes the self.camera_x in player innit
        self.player.collision_with_player(self.p2)
        self.player.update()

        alive_right = []
        alive_left = []
        logger.info(f"alive_right: {alive_right}, alive_left: {alive_left}")
        if not self.player.is_dead and not self.player.won:  # if the player alive
            alive_right.append(self.player.rect.right - self.camera_x)  # adds his right x to a list
            alive_left.append(self.player.rect.left - self.camera_x)  # adds his left x to a list

        if not self.p2.is_dead and not self.p2.won:
            alive_right.append(self.p2.rect.right - self.camera_x)
            alive_left.append(self.p2.rect.left - self.camera_x)
        logger.info(f"after update alive_right: {alive_right}, alive_left: {alive_left}")

        if alive_right:  # if this list not empty at least one player alive so also the left isn't empty
            leader_right = max(alive_right)
            trailer_left = min(alive_left)
            logger.info(f"leader_right: {leader_right}, trailer_left: {trailer_left}")

            if leader_right >= WINDOW_WIDTH * 0.85:  # if the leader is running out of space speed camera up
                self.camera_xchanger = 9

            elif trailer_left <= WINDOW_WIDTH * 0.25:  # if the trailer is running out of space slow camera down
                self.camera_xchanger = 3

            elif leader_right >= WINDOW_WIDTH * 0.75:  # if the leader is about to get close to run out of space speed
                self.camera_xchanger = 7  # up a little
            logger.info(f"camera_xchanger: {self.camera_xchanger}")
        # if not self.player.is_dead and not self.player.won:
        if not match_over:  # if match_over == false
            self.camera_x += self.camera_xchanger
            logger.info(f"camera_x: {self.camera_x}")
        if not self.player.is_dead and not self.player.won:  # if not dead and not won check:
            if self.player.rect.right < self.camera_x:
                self.player.die()

        self.window.fill('black')

        if hasattr(self, 'bg') and self.bg:  # cheks if there is an attribute bg and if not None
            bg_width = self.bg.get_width()

            for x in range(0, self.map_width, bg_width):
                self.window.blit(self.bg, (x - self.camera_x, 0))
            for sprite in self.all_sprites:

                if sprite == self.p2:
                    sprite.smoth_draw()

                    self.window.blit(sprite.image, (sprite.draw_x - self.camera_x, sprite.draw_y))

                else:
                    self.window.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
