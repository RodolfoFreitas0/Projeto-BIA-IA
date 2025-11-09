import pygame
import math
import random
import scripts.core.settings as settings

from scripts.headless.rectangle import Rectangle

class PhysicsEntity:

    # Inicializar a entidade
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.angle = 180
        self.speed = 0
        self.max_speed = 2
        self.acc = 0.1
        self.friction = 0.98

        self.HP = 1
        self.alive = True

    def update_logic(self, movement=(0, 0), angle=0):
        
        self.angle += angle
        self.angle %= 360
        self.angle_rad = math.radians(self.angle)
        
        if movement[0] > 0:
            self.angle += random.uniform(-0.3, 0.3)
            self.speed = min(self.speed + self.acc, self.max_speed)
        else:
            self.speed *= self.friction
        if movement[0] < 0:
            self.speed = max(self.speed - 0.02, -0.2)

        dx =  math.sin(self.angle_rad) * self.speed
        dy = -math.cos(self.angle_rad) * self.speed
        
        self.pos[1] += dx
        self.pos[0] += dy

        if self.HP <= 0:
            self.alive = False

    def render(self, surf, offset=(0, 0)):
        if not settings.PYGAME_MODE:
            return
        
        scaled_image = pygame.transform.scale(self.game.assets[self.type], (self.size[0] * 6, self.size[1] * 6))

        if self.type == "enemy":
            rotated_image= pygame.transform.rotate(scaled_image, self.angle + 90)
        else:
            rotated_image= pygame.transform.rotate(scaled_image, self.angle - 90)


        rect = rotated_image.get_rect(center=(self.pos[0] - offset[0], self.pos[1] - offset[1]))
        surf.blit(rotated_image, rect)

        if settings.DEBUG_MODE:
            if self.type == "player":
                color = (0, 255, 0)
            elif self.type == "enemy":
                color = (255, 0, 0)
            elif self.type == "bullet":
                color = (0, 0, 0)

            pygame.draw.rect(surf, color, self.rect().move(-offset[0], -offset[1]), 1)
    
    def rect(self):
        if settings.PYGAME_MODE:
            return pygame.Rect(
                self.pos[0] - self.size[0] - 2,
                self.pos[1] - (self.size[1] * 2 - 1),
                self.size[1] * 4,
                self.size[0] * 4
            )
        else:
            return Rectangle(
                self.pos[0] - self.size[0] - 2,
                self.pos[1] - (self.size[1] * 2 - 1),
                self.size[1] * 4,
                self.size[0] * 4
            )