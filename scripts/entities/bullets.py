import pygame
from .physics_entity import PhysicsEntity
from scripts.utills.debug import Debug
import scripts.core.settings as settings

class Bullet(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "bullet", pos, size)
        
        self.speed = self.max_speed = 6
        self.angle = game.player.angle
        self.lifetime = 180
        self.alive = True
    
    def outbounds(self, scroll, screen_width, screen_height):

        x_centro = scroll[0] + (screen_width // 2)
        y_centro = scroll[1] + (screen_height // 2)

        margem = 400

        limite_esquerda = x_centro - (screen_width // 2) - margem
        limite_direita = x_centro + (screen_width // 2) + margem
        limite_cima = y_centro - (screen_height // 2) - margem
        limite_baixo = y_centro + (screen_height // 2) + margem

        if (self.pos[0] < limite_esquerda or 
            self.pos[0] > limite_direita or 
            self.pos[1] < limite_cima or 
            self.pos[1] > limite_baixo):
            self.alive = False

    def update(self, display, scroll):
        super().update(movement=(1, 0))
        self.outbounds(scroll, display.get_width(), display.get_height())

        self.lifetime -= 1
        if self.lifetime == 0:
            self.alive = False

class BulletManager:
        def __init__(self, enemies):
            self.bullets = []
            self.enemies = enemies
            
        def add(self, bullet):
            self.bullets.append(bullet)

        def update(self, display, scroll):
            for bullet in self.bullets[:]:
                bullet.update(display, scroll)
                bullet.render(display, offset=scroll)

                if not bullet.alive:
                    self.bullets.remove(bullet)
                    continue

                for enemy in self.enemies:
                    if enemy.alive and bullet.rect().colliderect(enemy.rect()):
                        print("Bala colidiu com inimigo!")
                        enemy.alive = False
                        bullet.alive = False
                        self.bullets.remove(bullet)
                        break

                if settings.DEBUG_MODE:
                    Debug(f"Bullets: {len(self.bullets)}", 10, 50, display)