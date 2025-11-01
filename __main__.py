import pygame

from scripts.entities import Player
from scripts.entities import Bullet, BulletManager
from scripts.entities import EnemyManager

from scripts.utills.loader import load_img, load_imgs
from scripts.utills.debug import Debug

from scripts.visuals.clouds import Clouds

from scripts.core.camera import Camera
from scripts.core.events import handle_events
from scripts.core.hud import HUD
import scripts.core.settings as settings

class Game:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption(settings.CAPTION)
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # pygame.display.toggle_fullscreen()
        self.display = pygame.Surface(settings.DISPLAY_SIZE)

        self.game_active = True
        self.running = True

        self.clock = pygame.time.Clock()

        self.display_width = self.display.get_width()
        self.display_height = self.display.get_height()

        self.movement = [False, False]  # [left, right]
        self.rotation = [False, False]  # [counter-clockwise, clockwise]

        # Carregar assets
        self.assets = {
            "player": pygame.transform.rotate(load_img("kenney_pixelshmup/Ships/Ship_0000.png"), 0),
            "enemy": pygame.transform.rotate(load_img("kenney_pixelshmup/Tiles/tile_0012.png"), 0),
            "bullet": pygame.transform.rotate(load_img("kenney_pixelshmup/Tiles/tile_0009.png"), 0),
            "background": load_img("background.png"),
            "clouds": load_imgs("clouds")
        } 

        self.assets["background"] = pygame.transform.scale(self.assets["background"], settings.DISPLAY_SIZE)

        #Spawn dos inimigos
        self.enemy_manager = EnemyManager()
        pygame.time.set_timer(settings.SPAWN_EVENT, settings.SPAWN_TIME)

        self.score = 0
        self.highscore = 0
        pygame.time.set_timer(settings.SCORE_EVENT, settings.SCORE_TIME)

        self.clouds = Clouds(self.assets["clouds"], settings.CLOUD_COUNT) 

        self.player = Player(self, settings.PLAYER_START_POS, settings.PLAYER_SPEED)
        self.player.width = self.assets["player"].get_width()

        self.bullet_manager = BulletManager(self.enemy_manager.enemies)

        self.HUD = HUD(self)
        
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
            handle_events(self)        
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

                self.HUD.draw_score(self.display)
                self.HUD.draw_hp(self.display)

            else:
                handle_events(self)

                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0])

                self.display.blit(self.assets["background"], (0, 0))
                self.clouds.render(self.display, offset=self.render_scroll)

                self.HUD.draw_gameover(self.display)
                self.HUD.draw_highscore(self.display)
            
            if settings.DEBUG_MODE:
                Debug(f"FPS: {self.clock.get_fps():.1f}", 10, 10, self.display)
                Debug(f"Enemies: {self.enemy_manager.enemy_count}", 10, 20, self.display)
                Debug(f"CAM: (X: {self.CAM.scroll[0]:.2f}, Y: {self.CAM.scroll[1]:.2f})", 10, 30, self.display)
                Debug(f"POS: (X: {self.player.pos[0]:.2f}, Y: {self.player.pos[1]:.2f})", 10, 40, self.display)

            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update() 
            self.clock.tick(60)

# Def para iniciar o jogo
def main():
    game = Game()
    game.run()


# Chamando a def que inicia o jogo
if __name__ == "__main__":
    main()
