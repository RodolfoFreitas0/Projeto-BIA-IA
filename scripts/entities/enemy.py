import pygame
import random
import math

import scripts.core.settings as settings
from .physics_entity import PhysicsEntity

class Enemy(PhysicsEntity):

    def __init__(self, game, scroll, screen_width, screen_height, size):
        
        pos, side = self.spawn_pos(scroll, screen_width, screen_height)
        super().__init__(game, "enemy", pos, size)

        self.screenW = screen_width
        self.screenH = screen_height

        self.side = side
        self.enemies = []

        self.angle = self.random_angle(side)
        self.angle_rad = math.radians(self.angle)

        self.final_pos = (
            self.pos[0] - math.cos(self.angle_rad) * 6000,
            self.pos[1] + math.sin(self.angle_rad) * 6000
        )
        
        self.HP = 1

        self.acc = 10

    @classmethod
    def spawn_pos(cls, scroll, screen_width, screen_height):
        side = random.randint(0, 3)
        # side = ?

        x_centro = scroll[0] + (screen_width // 2)
        y_centro = scroll[1] + (screen_height // 2)

        margem = 100

        if side == 0: # Topo
            return [random.randint(
                x_centro - (screen_width // 2), x_centro + (screen_width // 2)),
                (y_centro - (screen_height // 2) - margem)], side
        
        elif side == 1: # Direita
            return [x_centro + (screen_width // 2) + margem,
                    random.randint(y_centro - (screen_height // 2), y_centro + (screen_height //2))], side
        
        elif side == 2: # Baixo
            return [random.randint(
                x_centro - (screen_width // 2), x_centro + (screen_width // 2)),
                y_centro + (screen_height //2)  + margem], side
        
        else: # Esquerda
            return [x_centro - (screen_width // 2)  - margem,
                    random.randint(y_centro -  (screen_height //2), y_centro + (screen_height // 2))], side
    
    def random_angle(self, side):

        if side == 0:  # Topo
            return random.uniform(105, 155)
        elif side == 1:  # Direita
            return random.uniform(335, 395) % 360
        elif side == 2:  # Baixo
            return random.uniform(215, 245)
        else:  # Esquerda
            return random.uniform(165, 195)

    def outbounds(self, scroll, screen_width, screen_height):

        x_centro = scroll[0] + (screen_width // 2)
        y_centro = scroll[1] + (screen_height // 2)

        margem = 400

        if self.side == 0:
            if self.pos[0] > x_centro + (screen_width // 2) + margem or self.pos[1] > y_centro + (screen_height // 2) + margem:
                self.alive = False
        elif self.side == 1:
            if self.pos[0] < x_centro - (screen_width // 2) - margem or self.pos[1] < y_centro - (screen_height // 2) - margem or self.pos[1] > y_centro + (screen_height // 2) + margem :
                self.alive = False
        elif self.side == 2:
            if self.pos[0] > x_centro + (screen_width // 2) + margem or self.pos[1] < y_centro - (screen_height // 2) - margem:
                self.alive = False
        elif self.side == 3:
            if self.pos[0] > x_centro + (screen_width // 2) + margem or self.pos[1] < y_centro - (screen_height // 2) - margem or self.pos[1] > y_centro + (screen_height // 2) + margem:
                self.alive = False

    
    def update_logic(self, surf, scroll):
        
        if self.side == 0 or self.side == 2:
            self.max_speed = 3

        if self.side == 1:
            self.max_speed = 1.8

        if self.side == 3:
            self.max_speed = 4.5

        self.angle += random.uniform(-0.3, 0.3)

        self.outbounds(scroll, self.screenH, self.screenW)
        
        super().update_logic(movement=(1,0))

        if settings.DEBUG_MODE and settings.PYGAME_MODE:
            pygame.draw.line(
                surf, (255, 0, 0),
                (self.pos[0] - scroll[0], self.pos[1] - scroll[1]),
                (self.final_pos[0] -  scroll[0], self.final_pos[1] - scroll[1]),
                1
            )
class EnemyManager:
        def __init__(self):
            self.enemies = []
            
        def add(self, enemy):
            self.enemies.append(enemy)

        def update_logic(self, display, scroll, player):
            for enemy in self.enemies[:]:
                enemy.update_logic(display, scroll)
                enemy.render(display, offset=scroll)
                
                # Remove inimigo caso ele morra
                if not enemy.alive:
                    self.enemies.remove(enemy)
                    continue

                    # Gameover caso o jogador toque no inimigo
                if settings.DEBUG_MODE == False:
                    if enemy.rect().colliderect(player.rect()):
                        print("Colided")
                        player.HP -= 1
                        self.enemies.remove(enemy)
                else:
                    if enemy.rect().colliderect(player.rect()):
                        print("Colided")
                        self.enemies.remove(enemy)

                
            self.enemy_count = len(self.enemies)
            if self.enemy_count > settings.MAX_ENEMIES:
                self.enemies.clear()