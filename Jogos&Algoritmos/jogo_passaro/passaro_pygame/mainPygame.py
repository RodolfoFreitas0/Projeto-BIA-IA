import pygame
import random
import sys

pygame.init()

try:
    from settings import *
except ImportError:
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    TITLE = "Flappy Bird"

try:
    from start_screen import StartScreen
except ImportError:
    class StartScreen:
        def __init__(self, screen, clock, title):
            pass
        def run(self):
            return "PLAY"

pygame.display.set_caption(TITLE)

class Bird:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = 150
        self.reset()

    def reset(self):
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        self.velocity = self.jump_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.y = int(self.y)

    def render(self):
        pygame.draw.rect(SCREEN, (255, 255, 0), self.rect)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 70
        self.gap_size = 170
        self.gap_y = random.randint(100, WINDOW_HEIGHT - 100 - self.gap_size)
        self.speed = 5
        self.passed = False
        
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + self.gap_size, self.width, WINDOW_HEIGHT - (self.gap_y + self.gap_size))

    def update(self):
        self.x -= self.speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x

    def render(self):
        pygame.draw.rect(SCREEN, (0, 200, 0), self.top_rect)
        pygame.draw.rect(SCREEN, (0, 200, 0), self.bottom_rect)

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
        self.bird = Bird()
        self.hud = HUD()
        self.score = 0
        self.game_over = False
        self.pipes = []
        self.spawn_timer = 0
        
        self.create_pipe()

    def create_pipe(self):
        self.pipes.append(Pipe(WINDOW_WIDTH))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_SPACE or event.key == pygame.K_w:
                self.bird.jump()

    def check_collisions(self):
        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= WINDOW_HEIGHT:
            self.game_over = True

        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                self.game_over = True

            if not pipe.passed and pipe.x + pipe.width < self.bird.rect.x:
                pipe.passed = True
                self.score += 1

    def update(self):
        self.bird.update()
        
        self.spawn_timer += 1
        if self.spawn_timer >= 80:
            self.create_pipe()
            self.spawn_timer = 0
            
        for pipe in self.pipes:
            pipe.update()
            
        self.pipes = [p for p in self.pipes if p.x + p.width > 0]
        
        self.check_collisions()

    def render(self):
        SCREEN.fill((0, 150, 200))
        
        for pipe in self.pipes:
            pipe.render()
        self.bird.render()
            
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