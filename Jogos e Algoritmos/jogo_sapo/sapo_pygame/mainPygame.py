import pygame
import random
import sys

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption(TITLE)

class Frog:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.speed = 40
        self.reset()
    
    def reset(self):
        start_x = random.randint(0, (WINDOW_WIDTH // 40) - 1) * 40
        self.rect = pygame.Rect(
            start_x, 
            WINDOW_HEIGHT - 60, 
            self.width, 
            self.height
        )

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WINDOW_WIDTH, self.rect.right)
        self.rect.bottom = min(WINDOW_HEIGHT, self.rect.bottom)

    def render(self):
        pygame.draw.rect(SCREEN, (0, 255, 0), self.rect)

class Obstacle:
    def __init__(self, x, y, width, direction, delay):
        self.rect = pygame.Rect(x, y, width, 40)
        self.direction = direction
        self.delay = delay
        self.timer = 0

    def update(self):
        self.timer += 1
        
        if self.timer >= self.delay:
            self.rect.x += self.direction * 40
            self.timer = 0
            
            if self.direction > 0 and self.rect.left > WINDOW_WIDTH:
                self.rect.right = -(random.randint(1, 5) * 40)
            elif self.direction < 0 and self.rect.right < 0:
                self.rect.left = WINDOW_WIDTH + (random.randint(1, 5) * 40)

    def render(self):
        pygame.draw.rect(SCREEN, (255, 0, 0), self.rect)

class HUD:
    def __init__(self):
        self.font_small = pygame.font.SysFont("Monocraft", 40)
        self.font_big = pygame.font.SysFont("Monocraft", 70)

    def draw_score(self, surf, score):
        score_text = self.font_small.render(f"SCORE: {score:02}", False, "white")
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
        self.frog = Frog()
        self.hud = HUD()
        self.score = 0
        self.game_over = False
        self.obstacles = []
        
        self.create_lanes()

    def create_lanes(self):
        lanes_y = [100, 140, 180, 220, 260, 340, 380, 420, 460, 500]
        
        for y in lanes_y:
            direction = random.choice([-1, 1])
            for _ in range(random.randint(2, 4)):
                x = random.randint(0, (WINDOW_WIDTH // 40) - 1) * 40
                delay = 15
                width = random.choice([40, 80, 120])
                self.obstacles.append(Obstacle(x, y, width, direction, delay))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.frog.move(0, -1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.frog.move(0, 1)
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self.frog.move(-1, 0)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self.frog.move(1, 0)

    def check_collisions(self):
        for obs in self.obstacles:
            if self.frog.rect.colliderect(obs.rect):
                self.game_over = True
                
        if self.frog.rect.top <= 60:
            self.score += 1
            self.frog.reset()
            self.obstacles.clear()
            self.create_lanes()

    def update(self):
        for obs in self.obstacles:
            obs.update()
        self.check_collisions()

    def render(self):
        SCREEN.fill((0, 0, 0))
        
        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(SCREEN, (255, 255, 255), screen_rect, 4)
        
        safe_zone_1 = pygame.Rect(0, WINDOW_HEIGHT - 180, WINDOW_WIDTH,  300)
        safe_zone_2 = pygame.Rect(0, 300, WINDOW_WIDTH, 40)
        safe_zone_3 = pygame.Rect(0, 0, WINDOW_WIDTH, 100)
        
        pygame.draw.rect(SCREEN, (20, 20, 20), safe_zone_1)
        pygame.draw.rect(SCREEN, (20, 20, 20), safe_zone_2)
        pygame.draw.rect(SCREEN, (20, 20, 20), safe_zone_3)

        self.frog.render()
        for obs in self.obstacles:
            obs.render()
            
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
                    self.handle_input(event)
            
            if not self.game_over:
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