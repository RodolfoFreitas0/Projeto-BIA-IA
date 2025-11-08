import time

from scripts.entities import Player
from scripts.entities import Bullet, BulletManager
from scripts.entities import EnemyManager

from scripts.utills.loader import load_img, load_imgs
from scripts.utills.debug import Debug

from scripts.visuals.clouds import Clouds

from scripts.core.camera import Camera
from scripts.core.events import handle_events
from scripts.core.hud import HUD
from scripts.core.controller import InputController

import scripts.core.settings as settings

class CoreGame:
    def __init__(self):

        self.game_active = True
        self.running = True

        self.time = 0
        self.clock = self.time.time()

        self.display_width = self.display.get_width()
        self.display_height = self.display.get_height()

        self.inputCTRL = InputController()

        #Spawn dos inimigos
        self.enemy_manager = EnemyManager()
        pygame.time.set_timer(settings.SPAWN_EVENT, settings.SPAWN_TIME)

        self.score = 0
        self.highscore = 0
        pygame.time.set_timer(settings.SCORE_EVENT, settings.SCORE_TIME)

        self.player = Player(self, settings.PLAYER_START_POS, settings.PLAYER_SPEED)
        self.player.width = 32

        self.bullet_manager = BulletManager(self.enemy_manager.enemies)
        
        self.CAM = Camera(self.player, (self.display_width, self.display_height))
        self.scroll = [0, 0]
        self.cooldown = 100

    def reset(self):
        self.enemy_manager.enemies.clear()
        pygame.time.set_timer(settings.SPAWN_EVENT, settings.SPAWN_TIME)

        self.movement = [False, False]
        self.rotation = [False, False]

        self.player.angle = 180
        self.player.pos[0] = 300 + self.scroll[0]
        self.player.pos[1] = 300 + self.scroll[1]
        self.player.HP = 3
        self.player.alive = True

        self.game_active = True
        self.score = 0

    def run(self):

        while self.running: 
            handle_events(self, self.inputCTRL)        
            if self.game_active == True:

                self.CAM.update()
                self.render_scroll = self.CAM.get_offset()

                self.display.blit(self.assets["background"], (0, 0))

                self.clouds.update()
                self.clouds.render(self.display, offset=self.render_scroll)
            
                rotation = (self.rotation[0] - self.rotation[1])
                
                player_screen_x = self.player.pos[0] - self.render_scroll[0]
                if player_screen_x + self.player.width + 40 < 0:
                    print("Saiu da tela")
                    self.player.HP -= 1
                    self.player.pos[0] = self.render_scroll[0] + 40
                    self.player.angle = 180
                        
                if self.score > self.highscore:
                     self.highscore = self.score

                self.enemy_manager.update(self.display, self.render_scroll, self.player)
                self.bullet_manager.update(self.display, self.render_scroll)

                self.player.update(((self.movement[1] - self.movement[0]), 0), rotation)
                self.player.render(self.display, offset=self.render_scroll)

                if self.player.shooting == True and self.cooldown >= 100:
                    bullet_pos = self.player.rect().center
                    bullet_size = (self.assets["bullet"].get_width() / 6, self.assets["bullet"].get_height() / 6)
                    new_bullet = Bullet(self, bullet_pos, bullet_size)
                    self.bullet_manager.add(new_bullet)
                    self.cooldown = 0

                self.cooldown += 10

                if self.player.alive == False:
                    self.game_active = False

            else:
                handle_events(self)

            self.clock.tick(60)