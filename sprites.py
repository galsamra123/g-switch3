from settings import *
import logging
logger = logging.getLogger(__name__)


class Sprite(pygame.sprite.Sprite):  # Simple base class for visible game objects.
    def __init__(self, pos, surf, groups):
        super().__init__(groups)  # adds the sprite to the group
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.last_rect = self.rect.copy()
