import pygame
import random
import sys
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

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
        
    def move(self, direction):
        if direction == 1:
            self.rect.x -= self.speed
        elif direction == 2:
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

class ArkanoidEnv:
    def __init__(self, render=False):
        self.render_mode = render
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        self.frame_skip = 4
        
        if self.render_mode:
            pygame.init()
            pygame.display.set_caption("Treino IA - Arkanoid")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 24)
            
        self.action_space = 3 
        
        self.observation_space = 5 + (BRICK_ROWS * BRICK_COLS)
        self.reset()

    def reset(self):
        self.paddle = Paddle()
        self.ball = Ball()
        self.score = 0
        self.frames = 0
        self.done = False
        
        self.bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                b_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
                b_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
                self.bricks.append(Brick(b_x, b_y))
                
        return self.get_state()

    def get_state(self):
        state = [
            self.paddle.rect.centerx / WINDOW_WIDTH,
            self.ball.rect.centerx / WINDOW_WIDTH,
            self.ball.rect.centery / WINDOW_HEIGHT,
            self.ball.dx / 10.0,
            self.ball.dy / 10.0
        ]
        
        for brick in self.bricks:
            state.append(1.0 if brick.active else 0.0)
            
        return state

    def step(self, action):
        total_reward = 0.0
        
        for _ in range(self.frame_skip):
            reward = 0.0
            self.frames += 1

            self.paddle.move(action)
            self.ball.update()

            reward -= 0.01

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
                self.done = True
                reward -= 40.0  
                
            if self.ball.rect.colliderect(self.paddle.rect) and self.ball.dy > 0:
                self.ball.rect.bottom = self.paddle.rect.top
                self.ball.dy *= -1
                
                hit_pos = (self.ball.rect.centerx - self.paddle.rect.centerx) / (self.paddle.width / 2)
                self.ball.dx = hit_pos * 6.0 
                reward += 10.0  

            hit_brick = False
            for brick in self.bricks:
                if brick.active and self.ball.rect.colliderect(brick.rect):
                    brick.active = False
                    hit_brick = True
                    self.score += 1
                    reward += 10.0  
                    break 
                    
            if hit_brick:
                self.ball.dy *= -1 
                
            active_bricks = sum(1 for b in self.bricks if b.active)
            if active_bricks == 0:
                self.done = True
                reward += 50.0

            total_reward += reward

            if self.render_mode:
                self.render()

            if self.done:
                break

        return self.get_state(), total_reward, self.done

    def render(self):
        if not self.render_mode:
            return
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((20, 20, 30))

        pygame.draw.rect(self.screen, (0, 150, 255), self.paddle.rect)
        
        pygame.draw.circle(self.screen, (255, 255, 255), self.ball.rect.center, self.ball.size // 2)

        for brick in self.bricks:
            if brick.active:
                pygame.draw.rect(self.screen, (255, 100, 100), brick.rect)
                pygame.draw.rect(self.screen, (200, 50, 50), brick.rect, 2)

        score_txt = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (10, 10))

        pygame.display.flip()
        self.clock.tick(60)