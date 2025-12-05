from .physics_entity import PhysicsEntity

import scripts.core.settings as settings
import random
import math

class Enemy(PhysicsEntity):

    def __init__(self, game, scroll, size):

        pos, side = self.spawn(scroll, settings.DISPLAY_SIZE[0], settings.DISPLAY_SIZE[1])
        super().__init__(game, "enemy", pos, size)
        
        self.side = side

        self.scroll = scroll

        self.angle = self.dif_angle(self.side)
        
        self.HP = 1
        self.max_speed = 3
        self.pos[0] = scroll[0] + settings.DISPLAY_SIZE[0] - 20
        self.timer = 0

        self.world_y = pos[1]
        self.fixed_x_offset = settings.DISPLAY_SIZE[0] - 20

    def spawn(self, scroll, screen_width, screen_height):
        side = random.randint(0, 2)
        margem = 20

        if side == 0: #Topo
            return [scroll[0] + screen_width - margem, margem + scroll[1]], side
        
        else: #Baixo 
            return [scroll[0] + screen_width - margem, scroll[1] + screen_width - margem], side
        
    def dif_angle(self, side):
        if side == 0: # Topo
            return 90
        else: # Baixo
            return -90

    def update_logic(self, scroll, player):

        if self.angle == 90: 
            self.world_y += self.speed
        else:
            self.world_y -= self.speed

        top = scroll[1] + 20
        bottom = scroll[1] + settings.DISPLAY_SIZE[1] - 20

        if self.world_y < top:
            self.world_y = top
            self.angle = 90

        elif self.world_y > bottom:
            self.world_y = bottom
            self.angle = 270

        self.pos[0] = scroll[0] + self.fixed_x_offset
        self.pos[1] = self.world_y

        # self.pos[0] = scroll[0] + settings.DISPLAY_SIZE[0] - 20

        # top = scroll[1] + 20
        # bottom = scroll[1] + settings.DISPLAY_SIZE[1] - 20

        # self.angle %= 360
        
        #     # Player descendo
        # if player.speed >= 1:
        #     if 185 <= player.angle <= 355:
        #         if self.angle == 90:   # Enemy subindo
        #             self.speed = 1.5
        #         else:
        #             self.speed = 4

        #     # Player subindo
        #     elif 5 <= player.angle <= 175:
        #         if self.angle == 270:  # Enemy descendo
        #             self.speed = 1.5
        #         else:
        #             self.speed = 4

        #     # Player indo frente/trás
        #     elif player.angle <= 5 or 175 <= player.angle <= 185 or player.angle >= 355:
        #             self.speed = 4.5
        # else:
        #     # Player parado
        #     self.speed = 1.5
        
        # if self.pos[1] > bottom:
        #     self.pos[1] = bottom - 10
        #     self.angle = -self.angle

        # elif self.pos[1] < top:
        #     self.pos[1] = top + 10
        #     self.angle = -self.angle

        # if self.angle == 90:
        #     self.pos[1] += self.speed
        # else:
        #     self.pos[1] -= self.speed
        
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        
        self.render_angle = math.degrees(math.atan2(dy, dx))
              
class EnemyManager:
        def __init__(self):
            self.enemies = []
            
        def add(self, enemy):
            self.enemies.append(enemy)

        def update_logic(self, scroll, player):
            for enemy in self.enemies:
                enemy.update_logic(scroll, player)
                
                if not enemy.alive:
                    self.enemies.remove(enemy)
                    continue

                if enemy.rect().colliderect(player.rect()):
                    print("Colided")
                    if not settings.DEBUG_MODE:
                        player.HP -= 1
                    self.enemies.remove(enemy)

            self.missile_count = len(self.enemies)
            if self.missile_count > settings.MAX_ENEMIES:
                self.enemies.clear()

        def render(self, display, scroll):
            if not settings.PYGAME_MODE:
                return
            
            for enemy in self.enemies:
                enemy.render(display, offset=scroll)
            
