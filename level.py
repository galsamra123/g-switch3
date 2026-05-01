from settings import *
import pygame
from sprites import  Sprite
from player import Player
import logging
logger = logging.getLogger(__name__)
class Level:
    def __init__(self, tmx_map):
        self.window = pygame.display.get_surface()
        self.all_sprites = pygame.sprite.Group()
        # creates List<Sprite> allSprites = new List<Sprite>();
        self.collisions_sprites = pygame.sprite.Group()
        self.death_sprites = pygame.sprite.Group()
        self.win_sprites = pygame.sprite.Group()
        self.setup(tmx_map)
        self.camera_x = 0
        self.camera_xchanger = 5

    def setup(self, tmx_map):
        logging.info("LAYERS:")
        for layer in tmx_map.layers:
            logger.info(f"{layer.name} {type(layer)}") # to see al the layer types in the map
        self.map_width = tmx_map.width * TILE_SIZE
        self.map_height = tmx_map.height * TILE_SIZE
        self.bg = tmx_map.get_layer_by_name('background').image

        for x, y, surf in tmx_map.get_layer_by_name('wall').tiles(): #print the walls to screen
            Sprite((x * TILE_SIZE , y * TILE_SIZE ), surf, (self.all_sprites, self.collisions_sprites))

        for x, y, surf in tmx_map.get_layer_by_name('death').tiles():
            Sprite((x * TILE_SIZE , y * TILE_SIZE ), surf, (self.all_sprites, self.death_sprites))

        for obj in tmx_map.get_layer_by_name('win'):
            Sprite((obj.x, obj.y),pygame.image.load('graphics/setpics/winflag.png').convert_alpha(),
                   (self.all_sprites, self.win_sprites))

        for obj in tmx_map.get_layer_by_name('player1'):
            self.player = Player((obj.x, obj.y), self.all_sprites, self.collisions_sprites, self.death_sprites,
                                 self.win_sprites,self.map_width,self.map_height)
            logger.info(f"x: {obj.x} y: {obj.y}")
    def run(self):
        self.all_sprites.update()
        if not self.player.is_dead and not self.player.won:
            self.camera_x += self.camera_xchanger
            if self.player.rect.right < self.camera_x:
                self.player.die()
            self.window.fill(('black'))
            if hasattr(self, 'bg') and self.bg:
                bg_width = self.bg.get_width()
                for x in range(0, self.map_width, bg_width):
                    self.window.blit(self.bg, (x - self.camera_x, 0))
                for sprite in self.all_sprites:
                    self.window.blit(sprite.image, (sprite.rect.x-self.camera_x, sprite.rect.y))