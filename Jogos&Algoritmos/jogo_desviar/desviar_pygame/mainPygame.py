import pygame
import random
import sys

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption(TITLE)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.speed = 7
        self.reset()
    
    def reset(self):
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 20,
            WINDOW_HEIGHT - 80,
            self.width,
            self.height
        )
        
    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WINDOW_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(WINDOW_HEIGHT, self.rect.bottom)
        
    def render(self):
        pygame.draw.rect(SCREEN, (0, 150, 255), self.rect)

class Enemy:
    def __init__(self):
        self.width = random.randint(30, 70)
        self.height = self.width
        self.rect = pygame.Rect(
            random.randint(0, WINDOW_WIDTH - self.width),
            -self.height,
            self.width,
            self.height
        )
        self.speed = random.uniform(4, 9)
        
    def update(self):
        self.rect.y += self.speed
        
    def render(self):
        pygame.draw.rect(SCREEN, (255, 50, 50), self.rect)

class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("Monocraft", 40)
        self.font_big = pygame.font.SysFont("Monocraft", 70)

    def draw_score(self, surf, score):
        score_text = self.font_small.render(f"SCORE: {score}", False, "white")
        text_rect = score_text.get_rect()
        
        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (20, 15)
        text_rect.center = background_rect.center

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(score_text, text_rect)

    def draw_game_over(self):
        SCREEN.fill((0, 0, 0))
        text = self.font_big.render("GAME OVER", True, "white")
        SCREEN.blit(text, text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))

        info = self.font_small.render("Aperte qualquer tecla para recomecar", True, "white")
        SCREEN.blit(info, info.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))

class Game:
    def __init__(self):
        self.player = Player()
        self.hud = HUD()
        self.enemies = []
        self.score = 0
        self.frames = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_rate = 15

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = 0
        
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            
        self.player.move(dx, dy)

    def check_collisions(self):
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.game_over = True

    def update(self):
        self.frames += 1
        
        if self.frames % 60 == 0:
            self.score += 1
            if self.frames % 300 == 0 and self.spawn_rate > 10:
                self.spawn_rate -= 2 

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.enemies.append(Enemy())
            self.spawn_timer = 0

        for enemy in self.enemies:
            enemy.update()

        self.enemies = [e for e in self.enemies if e.rect.top < WINDOW_HEIGHT]
        
        self.check_collisions()

    def render(self):
        SCREEN.fill((30, 30, 30))
        
        self.player.render()
        for enemy in self.enemies:
            enemy.render()
            
        self.hud.draw_score(SCREEN, self.score)

        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(SCREEN, (255, 255, 255), screen_rect, 4)

        pygame.display.update()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    return
                
                if self.game_over and event.type == pygame.KEYDOWN:
                    self.__init__()
            
            if not self.game_over:
                self.handle_input()
                self.update()
                self.render()
            else:
                self.hud.draw_game_over()
                pygame.display.update()
                
            CLOCK.tick(60)

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