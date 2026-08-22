import pygame
import random
import sys
import math

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption(TITLE)

BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_PADDING = 10
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = 45

class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.speed = 10
        self.reset()
        
    def reset(self):
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - self.width // 2,
            WINDOW_HEIGHT - 40,
            self.width,
            self.height
        )
        
    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WINDOW_WIDTH, self.rect.right)

class Ball:
    def __init__(self):
        self.size = 15
        self.speed = 7.0
        self.reset()
        
    def reset(self):
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - self.size // 2,
            WINDOW_HEIGHT // 2,
            self.size,
            self.size
        )
        angle = random.uniform(math.pi/4, 3*math.pi/4)
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.active = True

class Game():
    def __init__(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 24)
        self.running = True
        
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                b_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
                b_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
                self.bricks.append(Brick(b_x, b_y))

    def update(self):
        keys = pygame.key.get_pressed()
        self.paddle.move(keys)
        self.ball.update()

        if self.ball.rect.left <= 0:
            self.ball.rect.left = 0
            self.ball.dx *= -1
        elif self.ball.rect.right >= WINDOW_WIDTH:
            self.ball.rect.right = WINDOW_WIDTH
            self.ball.dx *= -1
            
        if self.ball.rect.top <= 0:
            self.ball.rect.top = 0
            self.ball.dy *= -1

        if self.ball.rect.bottom >= WINDOW_HEIGHT:
            self.running = False
            
        if self.ball.rect.colliderect(self.paddle.rect) and self.ball.dy > 0:
            self.ball.rect.bottom = self.paddle.rect.top
            self.ball.dy *= -1
            
            hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.width / 2)
            self.ball.dx = hit_pos * 6.0 

        hit_brick = False
        for brick in self.bricks:
            if brick.active and self.ball.rect.colliderect(brick.rect):
                brick.active = False
                hit_brick = True
                self.score += 1
                break 
                
        if hit_brick:
            self.ball.dy *= -1 
            
        active_bricks = sum(1 for b in self.bricks if b.active)
        if active_bricks == 0:
            self.running = False

    def render(self, surf):
        surf.fill((20, 20, 30))
        
        pygame.draw.rect(surf, (0, 150, 255), self.paddle.rect)
        pygame.draw.circle(surf, (255, 255, 255), self.ball.rect.center, self.ball.size // 2)

        for brick in self.bricks:
            if brick.active:
                pygame.draw.rect(surf, (255, 100, 100), brick.rect)
                pygame.draw.rect(surf, (200, 50, 50), brick.rect, 2)

        score_txt = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        surf.blit(score_txt, (10, 10))

        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surf, (255, 255, 255), screen_rect, 4)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.update()
            self.render(SCREEN)

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