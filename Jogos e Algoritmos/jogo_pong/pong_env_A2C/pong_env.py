import random

try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False

WIDTH, HEIGHT = 1280, 720

class GenericRect:
    def __init__(self, x, y, width, height):
        self._x = x
        self._y = y
        self.width = width
        self.height = height
        self._update_bounds()

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        self._update_bounds()

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        self._update_bounds()

    def colliderect(self, other):
        return (self.left < other.right and self.right > other.left and self.top < other.bottom and self.bottom > other.top)
    
    def clamp_ip(self, rect_bounds):
        if self.top < rect_bounds.top:
            self.y = rect_bounds.top
        if self.bottom > rect_bounds.bottom:
            self.y = rect_bounds.bottom - self.height
    
    def _update_bounds(self):
        self.left = self.x
        self.right = self.x + self.width
        self.top = self.y
        self.bottom = self.y + self.height
        self.centerx = self.x + self.width // 2
        self.centery = self.y + self.height // 2

class PongEnv:
    def __init__(self, render=False, player=False):
        self.render_mode = render
        self.player_mode = player

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
        Rect = pygame.Rect if self.render_mode else GenericRect

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

        if action_R == 1:
            self.AI.y -= 5
        elif action_R == 2:
            self.AI.y += 5
        elif action_R == 0:
            # reward_R -= 0.1
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
                # reward_L -= 0.1
                pass

        Rect_Bounds = pygame.Rect(0, 0, WIDTH, HEIGHT) if self.render_mode else GenericRect(0, 0, WIDTH, HEIGHT) 
        self.AI.clamp_ip(Rect_Bounds)
        self.player.clamp_ip(Rect_Bounds)

        # Punição por ficar perto das paredes, talvez ativar depois sei la
        # if self.AI.top <= 0 or self.AI.bottom >= HEIGHT:
        #     reward_R -= 0.1
        # if self.player.top <= 0 or self.player.bottom >= HEIGHT:
        #     reward_L -= 0.1

        distance_AI = abs(self.ball.centery - self.AI.centery)
        reward_R += max(0, 1.0 - (distance_AI / (HEIGHT // 2))) * 0.05

        distance_Player = abs(self.ball.centery - self.player.centery)
        reward_L += max(0, 1.0 - (distance_Player / (HEIGHT // 2))) * 0.05

        self.ball.x += self.ball_dx
        self.ball.y += self.ball_dy

        if self.ball.top <= 0:
            self.ball_dy *= -1

        if self.ball.bottom >= HEIGHT:
            self.ball_dy *= -1
        
        if self.ball.colliderect(self.AI):
            self.ball.right = self.AI.left
            self.ball_dx *= -1

            self.ball_dx *= random.uniform(0.98, 1.02)
            self.ball_dy *= random.uniform(0.98, 1.02)

            offset_AI = (self.ball.centery - self.AI.centery) / (self.AI.height / 2)
            self.ball_dy += offset_AI * 2
            reward_R += 5
            self.hits_R += 1
            # if abs(offset_AI) < 0.5:
            #     reward_R += 0.5
        
        if self.ball.colliderect(self.player):
            self.ball.left = self.player.right
            self.ball_dx *= -1
            self.ball_dx *= random.uniform(0.98, 1.02)
            self.ball_dy *= random.uniform(0.98, 1.02)
            offset_PL = (self.ball.centery - self.player.centery) / (self.player.height / 2)
            self.ball_dy += offset_PL * 2
            reward_L += 5
            self.hits_L += 1
            # if abs(offset_PL) < 0.5:
            #     reward_L += 0.5

        max_speed = 8
        self.ball_dx = max(-max_speed, min(max_speed, self.ball_dx))
        self.ball_dy = max(-max_speed, min(max_speed, self.ball_dy))
        
        if self.ball.right > WIDTH:
            if self.hits_L >= 1:
                self.player_score += 1
                reward_L += 10
                reward_R -= 10
            self.done = True
        
        if self.ball.left < 0:
            if self.hits_R >= 1:
                self.AI_score += 1
                reward_R += 10
                reward_L -= 10
            self.done = True

        # Talvez colocar isso depois, eles vão receber pontos por manter a bola na tela
        # reward_R += 0.001
        # reward_L += 0.001

        if self.render_mode:
            self.render()

        if not self.render_mode:
            self.AI._update_bounds()
            self.player._update_bounds()
            self.ball._update_bounds()
        
        if self.player_mode:
            return self.get_state(), reward_R, self.done
        
        state_R, state_L = self.get_state()
        return state_R, state_L, reward_R, reward_L, self.done
    
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
