import pygame
from .physics_entity import PhysicsEntity
from scripts.utills.debug import Debug
import scripts.core.settings as settings

class Bullet(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "bullet", pos, size)
        
        self.speed = self.max_speed = 6
        self.angle = game.player.angle
        self.alive = True
        self.lifetime = 60

    def update_logic(self, scroll):
        super().update_logic(movement=(1, 0))





class BulletManager:
        def __init__(self, enemies):
            self.bullets = []
            self.enemies = enemies
            
        def add(self, bullet):
            self.bullets.append(bullet)

        def update_logic(self, scroll):
            for bullet in self.bullets[:]:
                bullet.update_logic(scroll)

                bullet.lifetime -= 1
                if bullet.lifetime <= 0:
                    bullet.alive = False

                if not bullet.alive:
                    self.bullets.remove(bullet)
                    continue

                for enemy in self.enemies:
                    if settings.PYGAME_MODE == True:
                        if enemy.alive and bullet.rect().colliderect(enemy.rect()):
                            print("Bala colidiu com inimigo!")
                            enemy.alive = False
                            bullet.alive = False
                            self.bullets.remove(bullet)
                            break
                    else:
                         if enemy.alive and bullet.rect.colide(enemy.rect()):
                            print("Bala colidiu com inimigo!")
                            enemy.alive = False
                            bullet.alive = False
                            self.bullets.remove(bullet)
                            break
                                
        
        def render(self, display, scroll):
            if not settings.PYGAME_MODE:
                return

            for bullet in self.bullets:    
                bullet.render(display, scroll)

            if settings.DEBUG_MODE and settings.PYGAME_MODE:
                Debug(f"Bullets: {len(self.bullets)}", 10, 50, display)