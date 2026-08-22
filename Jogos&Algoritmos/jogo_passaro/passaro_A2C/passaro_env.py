import pygame
import random
import sys

try:
    pygame_available = True
except ImportError:
    pygame_available = False

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

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

class FlappyEnv:
    def __init__(self, render=False):
        self.render_mode = render
        
        if self.render_mode and not pygame_available:
            self.render_mode = False

        if self.render_mode:
            pygame.init()
            pygame.display.set_caption("Treino IA - Flappy")
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 30)

        self.action_space = 2
        self.observation_space = 5 
        
        self.reset()

    def reset(self):
        self.bird = Bird()
        self.pipes = [Pipe(WINDOW_WIDTH)]
        self.score = 0
        self.spawn_timer = 0
        self.done = False
        return self.get_state()

    def get_state(self):
        next_pipe = None
        for pipe in self.pipes:
            if pipe.x + pipe.width > self.bird.x:
                next_pipe = pipe
                break
                
        if next_pipe is None:
            pipe_x = WINDOW_WIDTH
            gap_top = WINDOW_HEIGHT // 2
            gap_bottom = WINDOW_HEIGHT // 2
        else:
            pipe_x = next_pipe.x
            gap_top = next_pipe.gap_y
            gap_bottom = next_pipe.gap_y + next_pipe.gap_size

        state = [
            self.bird.y / WINDOW_HEIGHT,
            self.bird.velocity / 15.0,
            (pipe_x - self.bird.x) / WINDOW_WIDTH,
            gap_top / WINDOW_HEIGHT,
            gap_bottom / WINDOW_HEIGHT
        ]
        return state

    def step(self, action):
        reward = 0.1
        
        if action == 1:
            self.bird.jump()

        self.bird.update()
        
        self.spawn_timer += 1
        if self.spawn_timer >= 80:
            self.pipes.append(Pipe(WINDOW_WIDTH))
            self.spawn_timer = 0
            
        for pipe in self.pipes:
            pipe.update()
            
        self.pipes = [p for p in self.pipes if p.x + p.width > 0]

        if self.bird.rect.top <= 0 or self.bird.rect.bottom >= WINDOW_HEIGHT:
            self.done = True
            reward = -5.0

        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                self.done = True
                reward = -5.0

            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
                reward = 1.0

        if self.render_mode:
            self.render()

        return self.get_state(), reward, self.done

    def render(self):
        if not self.render_mode or not pygame_available:
            return
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((0, 150, 200))
        
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (0, 200, 0), pipe.top_rect)
            pygame.draw.rect(self.screen, (0, 200, 0), pipe.bottom_rect)
            
        pygame.draw.rect(self.screen, (255, 255, 0), self.bird.rect)
        
        score_txt = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (10, 10))

        pygame.display.update()
        self.clock.tick(60)