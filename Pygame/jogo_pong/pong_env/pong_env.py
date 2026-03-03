import pygame
import random

WIDTH, HEIGHT = 1280, 720

class PongEnv:
    def __init__(self, render=False):
        self.render_mode = render

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
        
        self.reset()
    
    def reset(self):
        self.player = pygame.Rect(WIDTH-30, HEIGHT//2 - 50, 10, 100)
        self.enemy = pygame.Rect(20, HEIGHT//2 - 50, 10, 100)

        self.ball = pygame.Rect(WIDTH//2, HEIGHT//2, 10, 10)

        self.ball_dx = random.choice([-1, 1]) * random.uniform(2.5, 4)
        self.ball_dy = random.uniform(-3, 3)

        self.done = False
        return self.get_state()
    
    def step(self, action):

        prev_dist = abs(self.player.centery - self.ball.centery)

        reward = 0

        if action == 1:
            self.player.y -= 5
        elif action == 2:
            self.player.y += 5

        self.player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        if self.enemy.centery < self.ball.centery:
            self.enemy.y += 3
        elif self.enemy.centery > self.ball.centery:
            self.enemy.y -= 3

        self.enemy.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        if self.ball.top <= 0:
            self.ball.top = 0
            self.ball_dy *= -1

        if self.ball.bottom >= HEIGHT:
            self.ball.bottom = HEIGHT
            self.ball_dy *= -1
        
        if self.ball.colliderect(self.player):
            self.ball.right = self.player.left
            self.ball_dx *= -1

            self.ball_dx *= random.uniform(0.98, 1.02)
            self.ball_dy *= random.uniform(0.98, 1.02)

            offset = (self.ball.centery - self.player.centery) / (self.player.height / 2)
            self.ball_dy += offset * 2
            reward += 5
        
        if self.ball.colliderect(self.enemy):
            self.ball_dx *= -1
            self.ball_dx *= random.uniform(0.98, 1.02)
            self.ball_dy *= random.uniform(0.98, 1.02)

        max_speed = 6
        self.ball_dx = max(-max_speed, min(max_speed, self.ball_dx))
        self.ball_dy = max(-max_speed, min(max_speed, self.ball_dy))
        
        if self.ball.right > WIDTH:
            reward -= 25
            self.done = True
        
        if self.ball.left < 0:
            reward += 20
            self.done = True

        dist = abs(self.player.centery - self.ball.centery)

        if self.ball_dx > 0 and self.ball.x > WIDTH // 2:
            reward += 0.05 * (prev_dist - dist)

        if self.render_mode:
            self.render()
        
        return self.get_state(), reward, self.done
    
    def get_state(self):
        return [
            self.player.centery / HEIGHT,
            self.ball.x / WIDTH,
            self.ball.centery / HEIGHT,
            self.ball_dx / 5,
            self.ball_dy / 5,
            (self.ball.centery - self.player.centery) / HEIGHT
        ]

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        self.screen.fill((0, 0, 0))

        pygame.draw.rect(self.screen, (255, 255, 255), self.player)
        pygame.draw.rect(self.screen, (255, 255, 255), self.enemy)
        pygame.draw.rect(self.screen, (255, 255, 255), self.ball)

        pygame.display.flip()
        self.clock.tick(60)
