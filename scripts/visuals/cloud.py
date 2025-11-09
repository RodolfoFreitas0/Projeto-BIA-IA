import pygame
from scripts.core import settings

class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed 
        self.depth = depth

        scale = max(0.3, 1.5 - self.depth * 0.6)
        w = max(1, int(self.img.get_width() * scale))
        h = max(1, int(self.img.get_height() * scale))
        self.image = pygame.transform.scale(self.img, (w, h))

    def update(self):
        self.pos[0] += self.speed * self.depth
    
    def render(self, surf, offset=(0, 0)):
        if not settings.PYGAME_MODE:
            return

        render_pos = (
            self.pos[0] - offset[0] * self.depth,
            self.pos[1] - offset[1] * self.depth
        )
        
        img_w, img_h = self.image.get_size()

        surf.blit(self.image, (
            (render_pos[0] + img_w) % (surf.get_width() + self.image.get_width()) - img_w, 
            (render_pos[1] + img_h) % (surf.get_height() + self.image.get_height()) - img_h
        ))