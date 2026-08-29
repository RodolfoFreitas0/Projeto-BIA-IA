import random

try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False

WIDTH, HEIGHT = 1280, 720
MAX_BOUNCE_ANGLE_SPEED = 6

class PongEnv:
    def __init__(self, render=False, player=False, gamma=0.99):
        self.render_mode = render
        self.player_mode = player
        self.gamma = gamma

        self.AI_score = 0
        self.player_score = 0

        if self.render_mode and not pygame_available:
            print("Instale o pygame")
            self.render_mode = False

        if self.render_mode:
            pygame.init()
            if self.player_mode:
                pygame.display.set_caption("PLAYER vs IA")
            else:
                pygame.display.set_caption("Treinamento da IA")
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
        
        self.reset()
    
    def reset(self):
        Rect = pygame.Rect

        self.AI = Rect(WIDTH - 110, HEIGHT//2 - 50, 10, 100)
        self.player = Rect(110, HEIGHT//2 - 50, 10, 100)

        self.ball = Rect(WIDTH//2, HEIGHT//2, 10, 10)

        self.ball_dx = random.choice([-1, 1]) * random.uniform(2.5, 4)
        self.ball_dy = random.choice([-3, 3])

        if self.AI_score > 9 or self.player_score > 9:
            self.AI_score = 0
            self.player_score = 0

        self.done = False
        self.hits_R = 0
        self.hits_L = 0
        return self.get_state()
    
    def step(self, action_R, action_L=0):

        reward_L = 0
        reward_R = 0

        phi_R_before = self._alignment_potential(self.AI)
        phi_L_before = self._alignment_potential(self.player)

        if action_R == 1:
            self.AI.y -= 5
        elif action_R == 2:
            self.AI.y += 5
        elif action_R == 0:
            pass

        if self.player_mode:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.player.y -= 5
            if keys[pygame.K_s]:
                self.player.y += 5
        else:
            if action_L == 1:
                self.player.y -= 5
            elif action_L == 2:
                self.player.y += 5
            elif action_L == 0:
                pass

        Rect_Bounds = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.AI.clamp_ip(Rect_Bounds)
        self.player.clamp_ip(Rect_Bounds)

        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        if self.ball.top <= 0:
            self.ball.y = 0
            self.ball_dy *= -1

        if self.ball.bottom >= HEIGHT:
            self.ball.y = HEIGHT - self.ball.height
            self.ball_dy *= -1
        
        if self.ball.colliderect(self.AI):
            self.ball.right = self.AI.left
            self.ball_dx *= -1
            self.ball_dx *= random.uniform(1.0, 1.05)

            hit_y = self.ball.centery - self.AI.top
            relative_intersect = (hit_y - self.AI.height / 2) / (self.AI.height / 2)
            self.ball_dy = relative_intersect * MAX_BOUNCE_ANGLE_SPEED + random.uniform(-0.3, 0.3)

            if hit_y < 35 or hit_y > 65:
                reward_R += 0.2
            else:
                reward_R += 1.0
                
            self.hits_R += 1
        
        if self.ball.colliderect(self.player):
            self.ball.left = self.player.right
            self.ball_dx *= -1
            self.ball_dx *= random.uniform(1.0, 1.05)

            hit_y_pl = self.ball.centery - self.player.top
            relative_intersect_pl = (hit_y_pl - self.player.height / 2) / (self.player.height / 2)
            self.ball_dy = relative_intersect_pl * MAX_BOUNCE_ANGLE_SPEED + random.uniform(-0.3, 0.3)

            if hit_y_pl < 35 or hit_y_pl > 65:
                reward_L += 0.2
            else:
                reward_L += 1.0
                
            self.hits_L += 1

        max_speed = 8
        self.ball_dx = max(-max_speed, min(max_speed, self.ball_dx))
        self.ball_dy = max(-max_speed, min(max_speed, self.ball_dy))
        
        if self.ball.right > WIDTH:
            if self.hits_L >= 1:
                self.player_score += 1
            reward_R -= 1.0
            self.done = True
        
        if self.ball.left < 0:
            if self.hits_R >= 1:
                self.AI_score += 1
            reward_L -= 1.0
            self.done = True

        phi_R_after = 0.0 if self.done else self._alignment_potential(self.AI)
        phi_L_after = 0.0 if self.done else self._alignment_potential(self.player)

        reward_R += self.gamma * phi_R_after - phi_R_before
        reward_L += self.gamma * phi_L_after - phi_L_before

        if self.render_mode:
            self.render()
        
        if self.player_mode:
            return self.get_state(), reward_R, self.done
        
        state_R, state_L = self.get_state()
        return state_R, state_L, reward_R, reward_L, self.done

    def _alignment_potential(self, paddle):
        """Φ(s): quanto mais alinhado o centro da raquete está com o centro da
        bola, mais próximo de 0 (máximo); quanto mais desalinhado, mais negativo."""
        distance = abs(self.ball.centery - paddle.centery)
        return -(distance / (HEIGHT // 2))
    
    def get_state(self):
        state_R = [
            self.AI.centery / HEIGHT,
            self.ball.x / WIDTH,
            self.ball.centery / HEIGHT,
            self.ball_dx / 6,
            self.ball_dy / 6,
            (self.ball.centery - self.AI.centery) / HEIGHT,
            self.player.centery / HEIGHT
        ]

        state_L = [
            self.player.centery / HEIGHT,
            (WIDTH - self.ball.x) / WIDTH,
            self.ball.centery / HEIGHT,
            -self.ball_dx / 6,
            self.ball_dy / 6,
            (self.ball.centery - self.player.centery) / HEIGHT,
            self.AI.centery / HEIGHT
        ]

        if self.player_mode:
            return state_R
        
        return state_R, state_L

    def render(self):
        if not self.render_mode or not pygame_available:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        self.screen.fill((0, 0, 0))

        screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        pygame.draw.rect(self.screen, (255, 255, 255), screen_rect, 4)

        font_small = pygame.font.SysFont("Consolas", int(WIDTH/20))

        score_text = font_small.render(f"{self.player_score:02}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (WIDTH // 2 - 100, 15)

        text_rect.center = background_rect.center

        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), background_rect, 3)
        self.screen.blit(score_text, text_rect)

        score_text = font_small.render(f"{self.AI_score:02}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (WIDTH // 2 + 60, 15)

        text_rect.center = background_rect.center

        pygame.draw.rect(self.screen, (0, 0, 0), background_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), background_rect, 3)
        self.screen.blit(score_text, text_rect)

        pygame.draw.line(self.screen, "white",(WIDTH//2, 0),(WIDTH//2, HEIGHT),5)

        pygame.draw.rect(self.screen, (255, 255, 255), self.AI)
        pygame.draw.rect(self.screen, (255, 255, 255), self.player)
        pygame.draw.rect(self.screen, (255, 255, 255), self.ball)

        pygame.display.flip()
        self.clock.tick(60)