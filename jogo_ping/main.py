import pygame
import random
import sys

pygame.init()

from setttings import *

pygame.display.set_caption(TITLE)

class Platform:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 100)
        self.speed = 2
    
    def update_logic(self, key):
        if self.rect.top > 0 and key == "W" or self.rect.top > 0 and key == "UP":
            self.rect.y -= self.speed
        if self.rect.bottom < WINDOW_HEIGHT and key == "S" or self.rect.bottom < WINDOW_HEIGHT and key == "DOWN":
            self.rect.y += self.speed
    
    def render(self):
        pygame.draw.rect(SCREEN, "white", self.rect)

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(
            WINDOW_WIDTH/2 - 10,
            WINDOW_HEIGHT/2 - 10,
            10,
            10
        )
        self.reset()
    
    def reset(self, direction=None):
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.x_speed = random.choice([1, -1]) if direction is None else direction
        self.y_speed = random.choice([1, -1])
        self.speed = 2
    
    def update_logic(self):
        self.rect.x += self.x_speed * self.speed
        self.rect.y += self.y_speed * self.speed

        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.y_speed *= -1

    def collide(self, platform):
        if self.rect.colliderect(platform.rect):

            if self.rect.centery < platform.rect.top or self.rect.centery > platform.rect.bottom:
                self.y_speed *= -1
            else:
                self.x_speed *= -1
            
            if self.x_speed > 0:
                self.rect.left = platform.rect.right
            else:
                self.rect.right = platform.rect.left
    
    def render(self):
        pygame.draw.circle(SCREEN, "white", self.rect.center, 10)

class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("Monocraft", 30) 
        self.font_big = pygame.font.SysFont("Monocraft", 45)

    def draw_player_score(self, surf, score):

        score_text = self.font_small.render(f"{score}", False, "White")
        text_rect = score_text.get_rect()

        background_rect = pygame.Rect(WINDOW_WIDTH // 2 + 60, 15, 40, 40)
        text_rect.center = background_rect.center
        text_rect.centerx += 2

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(score_text, text_rect)
    
    def draw_enemy_score(self, surf, score):

        score_text = self.font_small.render(f"{score}", False, "White")
        text_rect = score_text.get_rect()

        background_rect = pygame.Rect(WINDOW_WIDTH // 2 - 100, 15, 40, 40)
        text_rect.center = background_rect.center
        text_rect.centerx += 2

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(score_text, text_rect)

class Game:
    def __init__(self):
        self.player = Platform(WINDOW_WIDTH - 110, WINDOW_HEIGHT/2 - 50)
        self.enemy = Platform(110, WINDOW_HEIGHT/2 - 50)
        self.ball = Ball()
        self.HUD = HUD()

        self.player_score = 0
        self.enemy_score = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.player.update_logic(key="W")
        if keys[pygame.K_s]:
            self.player.update_logic(key="S")
        
        if keys[pygame.K_UP]:
            self.enemy.update_logic(key="UP")
        if keys[pygame.K_DOWN]:
            self.enemy.update_logic(key="DOWN")
    
    def check_score(self):
        if self.ball.rect.x < -10:
            self.player_score += 1
            self.ball.reset(direction=-1)
        
        elif self.ball.rect.x > WINDOW_WIDTH + 10:
            self.enemy_score += 1
            self.ball.reset(direction=1)
        
    def update(self):
        self.ball.update_logic()
        self.ball.collide(self.player)
        self.ball.collide(self.enemy)
        self.check_score()

    def render(self):
        SCREEN.fill((0, 0, 0))

        pygame.draw.line(
            SCREEN, "white",
            (WINDOW_WIDTH//2, 0),
            (WINDOW_WIDTH//2, WINDOW_HEIGHT),
            5
        )

        self.player.render()
        self.enemy.render()
        self.ball.render()

        self.HUD.draw_player_score(SCREEN, self.player_score)
        self.HUD.draw_enemy_score(SCREEN, self.enemy_score)

        pygame.display.update()
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.handle_input()
            self.update()
            self.render()
            CLOCK.tick(300)

if __name__ == "__main__":
    game = Game()
    game.run()