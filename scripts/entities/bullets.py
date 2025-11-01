import pygame
from physics_entity import PhysicsEntity

class Bullets:
    def __init__(self, game, pos, size, speed):
        super().__init__(game, "bullet", pos, size)
    
    def update(self, movement=(0, 0)):
        super().update(tilemap, movement=movement)
