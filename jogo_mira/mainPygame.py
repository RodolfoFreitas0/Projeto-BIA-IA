import pygame
import sys
import random

pygame.init()

from settings import *
from start_screen import StartScreen
from jogo_ping.game_over import GameOver

pygame.display.set_caption(TITLE)

# --------------------------------------------------------------------------- #

class Game():
    def __init__(self):
        self.tmanager = TargetManager()
        self.hud = HUD()
        self.score = 0
        self.timer = 60 * 2
        self.game_over = False

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.tmanager.check_click(event.pos):
                    self.score += 1
        
        return True

    def update(self):
        if self.game_over:
            return
        
        self.timer -= 1

        if self.timer == 0:
            self.game_over = True
            return

        self.tmanager.spawn(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.tmanager.update(WINDOW_WIDTH, WINDOW_HEIGHT)

    def render(self):
        SCREEN.fill((0, 0, 0))
        self.tmanager.render(SCREEN, FONT)
        self.hud.timeHUD(SCREEN, self.timer // 60)
        self.hud.scoreHUD(SCREEN, WINDOW_WIDTH, self.score)

        pygame.display.update()

    def run(self):
        running = True

        while running:
            events = pygame.event.get()             

            running = self.handle_events(events)
            self.update()
            self.render()

            if self.game_over:
                return "GAME_OVER", self.score

            CLOCK.tick(60)

# --------------------------------------------------------------------------- #

class Target():
    def __init__(self, posX, posY, width, height, speedx, speedy):
        self.rect = pygame.Rect(posX, posY, width, height)
        self.speed_x = speedx
        self.speed_y = speedy
        self.lifetime = 60 * 4
    
    def update(self, window_width, window_height):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        self.lifetime -= 1

        if self.rect.left <= 0 or self.rect.right >= window_width:
            self.speed_x *= -1
        
        if self.rect.top <= 0 or self.rect.bottom >= window_height:
            self.speed_y *= -1
    
    def is_dead(self):
        return self.lifetime <= 61

    def render(self, surf, font):
        pygame.draw.rect(SCREEN, (255, 255, 255), self.rect, 0)

        seconds = int(self.lifetime / 60)
        text = font.render(f"{seconds}", False, "black")
        text_rect = text.get_rect()
        text_rect.centerx = self.rect.centerx + 4
        text_rect.centery = self.rect.centery

        surf.blit(text, text_rect)

# ---

class TargetManager():
    def __init__(self):
        self.targets = []

    def spawn(self, window_width, window_height):
        if len(self.targets) >= 3:
            return
        

        size = random.randint(75,175)
        speed_x = random.choice([-1, 0, 1])
        speed_y = random.choice([-1, 0, 1])

        x = random.randint(150, window_width - 150)
        y = random.randint(150, window_height - 150)

        self.targets.append(Target(x, y, size, size, speed_x, speed_y))
    
    def update(self, window_width, window_height):
        for target in self.targets[:]:
            target.update(window_width, window_height)
        
        self.targets = [t for t in self.targets if not t.is_dead()]
    
    def check_click(self, mouse_pos):
        for target in self.targets[:]:
            if target.rect.collidepoint(mouse_pos):
                self.targets.remove(target)
                return True
        return False

    def render(self, surf, font):
        for target in self.targets[:]:
            target.render(surf, font)

# --------------------------------------------------------------------------- #

class HUD():
    def __init__(self):
        self.font_small = pygame.font.SysFont("Monocraft", 40) 
        self.font_big = pygame.font.SysFont("Monocraft", 50)

    def scoreHUD(self, surf, window_width, score):

        score_text = self.font_small.render(f"{score:03}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (window_width - 120, 15)

        text_rect.centerx = background_rect.centerx + 3
        text_rect.centery = background_rect.centery

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(score_text, text_rect)

    def timeHUD(self, surf, time):

        time_text = self.font_small.render(f"{time:02}", False, "white")
        text_rect = time_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (50, 15)

        text_rect.centerx = background_rect.centerx + 3
        text_rect.centery = background_rect.centery

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(time_text, text_rect)
    
# --------------------------------------------------------------------------- #

if __name__ == "__main__":

    highscore = 0

    while True:
        start = StartScreen(SCREEN, CLOCK, TITLE)
        result = start.run()

        if result == "PLAY":

            game = Game()
            result, score = game.run()

            if result == "GAME_OVER":
                if score > highscore:
                    highscore = score

                gameover = GameOver(score, highscore)
                action = gameover.run()

                if action == "RESTART":
                    continue
                elif action == "MENU":
                    continue

        elif result == "QUIT":
            break