import pygame
import random
import sys
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
MAX_ENEMIES_IN_STATE = 5 

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.speed = 7
        self.reset()
    
    def reset(self):
        self.rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 20,
            WINDOW_HEIGHT - 80,
            self.width,
            self.height
        )
        
    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WINDOW_WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(WINDOW_HEIGHT, self.rect.bottom)

class Enemy:
    def __init__(self):
        self.width = random.randint(30, 70)
        self.height = self.width
        self.rect = pygame.Rect(
            random.randint(0, WINDOW_WIDTH - self.width),
            -self.height,
            self.width,
            self.height
        )
        self.speed = random.uniform(4, 9)
        
    def update(self):
        self.rect.y += self.speed

class DodgerEnv:
    def __init__(self, render=False):
        self.render_mode = render
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        
        if self.render_mode:
            pygame.init()
            pygame.display.set_caption("Treino IA - Dodger Zone")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 24)
            
        self.action_space = 5
        self.observation_space = 4 + (MAX_ENEMIES_IN_STATE * 4)
        self.reset()

    def reset(self):
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.frames = 0
        self.spawn_timer = 0
        self.spawn_rate = 15
        self.done = False
        
        self.zone_size = 150
        self.zone_timer = 0
        self.zone_rect = pygame.Rect(0, 0, self.zone_size, self.zone_size)
        self.move_zone()
        
        return self.get_state()
        
    def move_zone(self):
        min_dist = 250
        
        while True:
            new_x = random.randint(0, self.window_width - self.zone_size)
            new_y = random.randint(0, self.window_height - self.zone_size)
            
            center_x = new_x + (self.zone_size // 2)
            center_y = new_y + (self.zone_size // 2)
            
            dist = math.hypot(self.player.rect.centerx - center_x, 
                              self.player.rect.centery - center_y)
            
            if dist >= min_dist:
                self.zone_rect.x = new_x
                self.zone_rect.y = new_y
                break

    def get_state(self):
        state = [
            self.player.rect.centerx / WINDOW_WIDTH,
            self.player.rect.centery / WINDOW_HEIGHT,
            (self.zone_rect.centerx - self.player.rect.centerx) / WINDOW_WIDTH,
            (self.zone_rect.centery - self.player.rect.centery) / WINDOW_HEIGHT
        ]
        
        sorted_enemies = sorted(self.enemies, key=lambda e: math.hypot(e.rect.centerx - self.player.rect.centerx, e.rect.centery - self.player.rect.centery))
        
        for i in range(MAX_ENEMIES_IN_STATE):
            if i < len(sorted_enemies):
                e = sorted_enemies[i]
                state.extend([
                    (e.rect.centerx - self.player.rect.centerx) / WINDOW_WIDTH,
                    (e.rect.centery - self.player.rect.centery) / WINDOW_HEIGHT,
                    e.width / 100.0,
                    e.speed / 10.0
                ])
            else:
                state.extend([0.0, 0.0, 0.0, 0.0])
                
        return state

    def step(self, action):
        reward = 0.0
        self.frames += 1
        
        dx = 0
        dy = 0

        dist_old = math.hypot(self.player.rect.centerx - self.zone_rect.centerx, self.player.rect.centery - self.zone_rect.centery)

        if action == 1: dy = -1
        elif action == 2: dy = 1
        elif action == 3: dx = -1
        elif action == 4: dx = 1    
        
        self.player.move(dx, dy)

        dist_new = math.hypot(self.player.rect.centerx - self.zone_rect.centerx, self.player.rect.centery - self.zone_rect.centery)

        if self.player.rect.left <= 0 or self.player.rect.right >= WINDOW_WIDTH:
            reward -= 0.5
        if self.player.rect.top <= 0 or self.player.rect.bottom >= WINDOW_HEIGHT:
            reward -= 0.5

        self.zone_timer += 1
        if self.zone_timer >= 300:
            self.move_zone()
            self.zone_timer = 0
            
        if self.player.rect.colliderect(self.zone_rect):
            reward += 0.2
            if self.frames % 30 == 0:
                self.score += 1
        else:
            if dist_new < dist_old:
                reward += 0.05
            elif dist_new > dist_old:
                reward -= 0.05

            reward -= 0.01
            
        if self.frames % 300 == 0 and self.spawn_rate > 10:
            self.spawn_rate -= 2 

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.enemies.append(Enemy())
            self.spawn_timer = 0

        for enemy in self.enemies:
            enemy.update()

        self.enemies = [e for e in self.enemies if e.rect.top < WINDOW_HEIGHT]
        
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.done = True
                reward = -50.0
                break

        if self.render_mode:
            self.render()
            
        return self.get_state(), reward, self.done

    def render(self):
        if not self.render_mode:
            return
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        self.screen.fill((30, 30, 30))
        
        pygame.draw.rect(self.screen, (0, 255, 0), self.zone_rect, 3)
        
        pygame.draw.rect(self.screen, (0, 150, 255), self.player.rect)
        for enemy in self.enemies:
            pygame.draw.rect(self.screen, (255, 50, 50), enemy.rect)
            
        score_txt = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_txt, (10, 10))

        pygame.display.flip()
        self.clock.tick(60)