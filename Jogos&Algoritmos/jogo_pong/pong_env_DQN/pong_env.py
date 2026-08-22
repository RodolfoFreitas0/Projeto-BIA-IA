import pygame
import random

WIDTH, HEIGHT = 1280, 720

class PongEnv:
    def __init__(self, render=False, player=False):
        self.render_mode = render
        self.player_mode = player

        self.AI_score = 0
        self.player_score = 0

        if self.player_mode:
            pygame.display.set_caption("PLAYER vs IA")
        else:
            pygame.display.set_caption("Treinamento da IA")

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
        
        self.reset()
    
    def reset(self):
        self.AI = pygame.Rect(WIDTH - 110, HEIGHT//2 - 50, 10, 100)
        self.player = pygame.Rect(110, HEIGHT//2 - 50, 10, 100)

        self.ball = pygame.Rect(WIDTH//2, HEIGHT//2, 10, 10)

        self.ball_dx = random.choice([-1, 1]) * random.uniform(2.5, 4)
        self.ball_dy = random.uniform(-3, 3)

        if self.AI_score > 9 or self.player_score > 9:
            self.AI_score = 0
            self.player_score = 0

        self.done = False
        return self.get_state()
    
    def step(self, action):

        reward = 0

        if action == 1:
            self.AI.y -= 5
        elif action == 2:
            self.AI.y += 5

        self.AI.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

        if not self.player_mode:
            if self.player.centery < self.ball.centery:
                self.player.y += 3
            elif self.player.centery > self.ball.centery:
                self.player.y -= 3
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player.y -= 5
            if keys[pygame.K_s]:
                self.player.y += 5


        self.player.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        
        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        if self.ball.top <= 0:
            self.ball.top = 2
            self.ball_dy *= -1

        if self.ball.bottom >= HEIGHT:
            self.ball.bottom = HEIGHT - 2
            self.ball_dy *= -1
        
        if self.ball.colliderect(self.AI):
            self.ball.right = self.AI.left
            self.ball_dx *= -1

            self.ball_dx *= random.uniform(0.98, 1.02)
            self.ball_dy *= random.uniform(0.98, 1.02)

            offset_AI = (self.ball.centery - self.AI.centery) / (self.AI.height / 2)
            self.ball_dy += offset_AI * 2
            reward += 20
        
        if self.ball.colliderect(self.player):
            self.ball.left = self.player.right
            self.ball_dx *= -1
            self.ball_dx *= random.uniform(0.98, 1.02)
            self.ball_dy *= random.uniform(0.98, 1.02)
            offset_PL = (self.ball.centery - self.player.centery) / (self.player.height / 2)
            self.ball_dy += offset_PL * 2

        max_speed = 6
        self.ball_dx = max(-max_speed, min(max_speed, self.ball_dx))
        self.ball_dy = max(-max_speed, min(max_speed, self.ball_dy))
        
        if self.ball.right > WIDTH:
            self.player_score += 1
            reward -= 25
            self.done = True
        
        if self.ball.left < 0:
            self.AI_score += 1
            reward += 20
            self.done = True

        if self.render_mode:
            self.render()
        
        return self.get_state(), reward, self.done
    
    def get_state(self):
        return [
            self.AI.centery / HEIGHT,
            self.ball.x / WIDTH,
            self.ball.centery / HEIGHT,
            self.ball_dx / 5,
            self.ball_dy / 5,
            (self.ball.centery - self.AI.centery) / HEIGHT
        ]

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        self.screen.fill((0, 0, 0))

        screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, (255, 255, 255), screen_rect, 4)

        font_small = pygame.font.SysFont("Consolas", int(WIDTH/20))

        # -----------------

        score_text = font_small.render(f"{self.player_score:02}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (WIDTH // 2 - 100, 15)

        text_rect.center = background_rect.center

        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), background_rect, 3)
        self.screen.blit(score_text, text_rect)

        # -----------------

        score_text = font_small.render(f"{self.AI_score:02}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (WIDTH // 2 + 60, 15)

        text_rect.center = background_rect.center

        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), background_rect, 3)
        self.screen.blit(score_text, text_rect)

        # -----------------

        pygame.draw.line(self.screen, "white",(WIDTH//2, 0),(WIDTH//2, HEIGHT),5)

        pygame.draw.rect(self.screen, (255, 255, 255), self.AI)
        pygame.draw.rect(self.screen, (255, 255, 255), self.player)
        pygame.draw.rect(self.screen, (255, 255, 255), self.ball)

        pygame.display.flip()
        self.clock.tick(60)
