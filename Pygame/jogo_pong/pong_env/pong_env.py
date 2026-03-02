import pygame
import random

WIDTH, HEIGHT = 1280, 720

class PongEnv:
    def __init__(self, render=False):
        self.render_mode = False

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
        
        self.reset()
    
    def reset(self):
        self.player = pygame.Rect(WIDTH-30, HEIGHT//2 - 50, 10, 100)
        self.enemy = pygame.rect(20, HEIGHT//2 -50, 10, 100)

        self.ball = pygame.rect(WIDTH//2, HEIGHT//2, 10, 10)

        self.ball_dx = random.choice([-1, 1]) * 3
        self.ball_dy = random.choice([-1, 1]) * 3

        self.done = False
        return self.get_state()
    
    def step(self, action):

        reward = 0

        if action == 1:
            self.player.y -= 5
        elif action == 2:
            self.player.y += 5
        
        if self.enemy.centery < self.ball.centery:
            self.enemy.y += 3
        elif self.enemy.centery > self.ball.centery:
            self.enemy.y -= 3
        
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        if self.ball.top <= 0 or self.ball.bottom >= HEIGHT:
            self.ball_dy *= -1
        
        if self.ball.colliderect(self.player):
            self.ball_dx *= -1
            reward += 5
        
        if self.ball.colliderect(self.enemy):
            self.ball_dx *= -1s
        
        if self.ball.right > WIDTH:
            reward -= 20
            self.done = True
        
        if self.ball.left < 0:
            reward += 20
            self.done = True
        
        reward += 0.01

        if self.render_mode:
            self.render()
        
        return self.get_state(), reward, self.done
    
    def get_state(self):
        return [
            self.player.y / HEIGHT,
            self.enemy.y / HEIGHT,
            self.ball.x / HEIGHT,
            self.ball.y / HEIGHT,
            self.ball_dx / 5,
            self.ball_dy / 5
        ]

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        self.screen.fill(0, 0, 0)

        pygame.draw.rect(self.screen, (255, 255, 255), self.player)
        pygame.draw.rect(self.screen, (255, 255, 255), self.enemy)
        pygame.draw.rect(self.screen, (255, 255, 255), self.ball)

        pygame.display.flip()
        self.clock.tick(60)
