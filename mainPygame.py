import pygame
import time

from scripts.entities import Player
from scripts.entities import Bullet, BulletManager
from scripts.entities import EnemyManager

from scripts.utills import load_img, load_imgs
from scripts.utills import Debug
from scripts.utills import SimpleClock

from scripts.visuals import Clouds

from scripts.core import Camera
from scripts.core import handle_events
from scripts.core import HUD
from scripts.core import InputController

import scripts.core.settings as settings

class PygameGame:
    def __init__(self):

        if settings.PYGAME_MODE:
            pygame.init()
            pygame.display.set_caption(settings.CAPTION)
            self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
            # pygame.display.toggle_fullscreen()
            self.display = pygame.Surface(settings.DISPLAY_SIZE)
            self.clock = pygame.time.Clock()
        else:
            self.screen = None
            self.display = None
            self.clock = SimpleClock()

        self.game_active = True
        self.running = True

        self.display_width = settings.DISPLAY_SIZE[0]
        self.display_height = settings.DISPLAY_SIZE[1]

        self.inputCTRL = InputController()

        # Carregar assets
        if settings.PYGAME_MODE:
            self.assets = {
                "player": pygame.transform.rotate(load_img("kenney_pixelshmup/Ships/Ship_0000.png"), 0),
                "enemy": pygame.transform.rotate(load_img("kenney_pixelshmup/Tiles/tile_0012.png"), 0),
                "bullet": pygame.transform.rotate(load_img("kenney_pixelshmup/Tiles/tile_0009.png"), 0),
                "background": load_img("background.png"),
                "clouds": load_imgs("clouds")
            } 
            self.assets["background"] = pygame.transform.scale(self.assets["background"], settings.DISPLAY_SIZE)
        else:
            self.assets = {}

        self.enemy_manager = EnemyManager()
        self.bullet_manager = BulletManager(self.enemy_manager.enemies)
        self.player = Player(self, settings.PLAYER_START_POS, settings.PLAYER_SPEED)
       
        self.HUD = HUD(self)
        self.CAM = Camera(self.player, (self.display_width, self.display_height))
        self.clouds = Clouds(self.assets["clouds"], settings.CLOUD_COUNT) if settings.PYGAME_MODE else None
        self.scroll = [0, 0]
        self.cooldown = 100
        self.score = 0
        self.highscore = 0

        if settings.PYGAME_MODE:
            pygame.time.set_timer(settings.SPAWN_EVENT, settings.SPAWN_TIME)
            pygame.time.set_timer(settings.SCORE_EVENT, settings.SCORE_TIME)

    def reset(self):
        self.enemy_manager.enemies.clear()
        pygame.time.set_timer(settings.SPAWN_EVENT, settings.SPAWN_TIME)

        self.inputCTRL.reset()

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

                self.CAM.update_logic()
                self.render_scroll = self.CAM.get_offset()

                if settings.PYGAME_MODE:
                    self.display.blit(self.assets["background"], (0, 0))

                if settings.PYGAME_MODE:
                    self.clouds.update()
                    self.clouds.render(self.display, offset=self.render_scroll)
                

                rotation = self.inputCTRL.rotation_value()
                
                player_screen_x = self.player.pos[0] - self.render_scroll[0]
                if player_screen_x + 80 < 0:
                    print("Saiu da tela")
                    self.player.HP -= 1
                    self.player.pos[0] = self.render_scroll[0] + 40
                    self.player.angle = 180
                        
                if self.score > self.highscore:
                     self.highscore = self.score

                self.enemy_manager.update_logic(self.render_scroll, self.player)
                self.enemy_manager.render(self.display, self.render_scroll)

                self.bullet_manager.update_logic()
                self.bullet_manager.render(self.display, self.render_scroll)

                self.player.update_logic(((self.inputCTRL.movement[1] - self.inputCTRL.movement[0]), 0), rotation)
                self.player.render(self.display, offset=self.render_scroll)

                if self.inputCTRL.shooting and self.cooldown >= 100:
                    bullet_pos = self.player.rect().center
                    bullet_size = (2, 2)
                    new_bullet = Bullet(self, bullet_pos, bullet_size)
                    self.bullet_manager.add(new_bullet)
                    self.cooldown = 0

                self.cooldown += 10

                if self.player.alive == False:
                    self.game_active = False

                self.HUD.draw_score(self.display)
                self.HUD.draw_hp(self.display)

            else:

                self.scroll[0] += (self.player.rect().centerx - self.display_width / 2 - self.scroll[0])
                
                if settings.PYGAME_MODE:
                    self.display.blit(self.assets["background"], (0, 0))
                    self.clouds.render(self.display, offset=self.render_scroll)
                    self.HUD.draw_gameover(self.display)
                    self.HUD.draw_highscore(self.display)
            
            if settings.DEBUG_MODE and settings.PYGAME_MODE:
                Debug(f"FPS: {self.clock.get_fps():.1f}", 10, 10, self.display)
                Debug(f"Enemies: {self.enemy_manager.enemy_count}", 10, 20, self.display)
                Debug(f"CAM: (X: {self.CAM.scroll[0]:.2f}, Y: {self.CAM.scroll[1]:.2f})", 10, 30, self.display)
                Debug(f"POS: (X: {self.player.pos[0]:.2f}, Y: {self.player.pos[1]:.2f})", 10, 40, self.display)

            if settings.PYGAME_MODE:
                self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
                pygame.display.update() 
                self.clock.tick(60)
            else:
                self.clock.tick(60) 
                if settings.DEBUG_MODE:
                    print(f"Fps: {self.clock.get_fps():.1f}")
                    print(f"POS: (X: {self.player.pos[0]:.2f}, Y: {self.player.pos[1]:.2f})")
                    print(f"Hp: {self.player.HP}")

                    settings.DEBUG_MODE == False

def __main__():
    game = PygameGame()
    game.run()


# Chamando a def que inicia o jogo
if __name__ == "__main__":
    __main__()