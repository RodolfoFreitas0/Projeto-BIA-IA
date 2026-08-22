import pygame
import sys
import random

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption(TITLE)

class Game():
    def __init__(self):
        self.player = Player(50, WINDOW_HEIGHT // 2, 20, 20)
        self.obsmanager = Obstacle_Manager(self)
        self.hud = HUD()
        self.gameover = False
        self.score = 0
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.gameover == True:
                    self.score = 0
                    self.gameover = False
                    return
                
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return False
            
        return True

    def update(self, events):
        self.player.update(events)
        self.obsmanager.update(self.player)

    def render(self, surf):
        surf.fill((0, 0, 0))

        pygame.draw.line(surf, (255, 255, 255), (-40, WINDOW_HEIGHT // 2 + 62), (WINDOW_WIDTH + 40, WINDOW_HEIGHT // 2 + 62), 5)

        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surf, (255, 255, 255), screen_rect, 4)
        
        self.obsmanager.render(surf)
        self.player.render(surf)

    def run(self):
        running = True
        
        while running:

            events = pygame.event.get()

            running = self.handle_events(events)

            if self.gameover == False:
                self.update(events)
                self.render(SCREEN)
                self.hud.score_hud(self.score, SCREEN)
            else:
                self.render(SCREEN)
                self.hud.gameover_hud(self.score, SCREEN)

            pygame.display.update()
            CLOCK.tick(60)

class Player():
    def __init__(self, posX, posY, width, height):
        self.rect = pygame.Rect(posX, posY, width, height)

        self.speed_y = 0
        self.gravity = 0.65
        self.jump_force = -10

        self.on_ground = False

        self.ground_y = WINDOW_HEIGHT // 2 + 40
    
    def update(self, events):
        self.speed_y += self.gravity

        self.rect.y += self.speed_y

        if self.rect.y >= self.ground_y:
            self.rect.y = self.ground_y
            self.speed_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.on_ground:
                    self.speed_y = self.jump_force

    def render(self, surf):
        pygame.draw.rect(surf, (255, 255 ,255), self.rect, 0)

class Obstacle():
    def __init__(self):
        width = random.choice([2, 4, 6])
        self.rect = pygame.Rect(WINDOW_WIDTH + 30, WINDOW_HEIGHT // 2 + 40, width * 10, 20)
        self.speed_x = 5
    
    def is_out(self):
        return self.rect.x < -60

    def update(self):
        self.rect.x -= self.speed_x

    def render(self, surf):
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 0)

class Obstacle_Manager():
    def __init__(self, game):
        self.obstacles = []
        self.timer = 1200
        self.game = game

    def spawn(self):
        self.obstacles.append(Obstacle())

    def update(self, player):
        self.timer -= 10

        if self.timer <= 0:
            self.spawn()
            self.timer = random.randint(300, 800)
    
        for obstacle in self.obstacles[:]:
            if obstacle.rect.x == player.rect.x:
                self.game.score += 1

            if obstacle.rect.colliderect(player.rect):
                self.game.gameover = True

            obstacle.update()
        
        self.obstacles = [obs for obs in self.obstacles if not obs.is_out()]

    def render(self, surf):
        for obstacle in self.obstacles[:]:
            obstacle.render(surf)

class HUD():
    def __init__(self):
        self.font_big = pygame.font.SysFont("Monocraft", 40) 
        self.font_small = pygame.font.SysFont("Monocraft", 20)

    def score_hud(self, score, surf):
        score_text = self.font_big.render(f"{score:02}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (15, 15)

        text_rect.centerx = background_rect.centerx + 2
        text_rect.centery = background_rect.centery

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(score_text, text_rect)
    
    def gameover_hud(self, score, surf):

        text = self.font_big.render(f"Pontuação: |{score}|", True, "white")
        surf.blit(text, text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 100)))

        info = self.font_small.render(f"Aperte qualquer tecla para voltar ao menu", True, "white")
        surf.blit(info, info.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))

if __name__ == "__main__":

    while True:
        start = StartScreen(SCREEN, CLOCK, TITLE)
        result = start.run()

        if result == "PLAY":
            game = Game()
            game.run()
        else:
            break
        
    pygame.quit()
    sys.exit()