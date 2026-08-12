import pygame
import random
import sys
import math

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MAX_TARGETS = 3
CURSOR_SPEED = 15

class Target:
    def __init__(self, posX, posY, width, height, speedx, speedy):
        self.rect = pygame.Rect(posX, posY, width, height)
        self.speed_x = speedx
        self.speed_y = speedy
        self.max_lifetime = 60 * 4
        self.lifetime = self.max_lifetime

    def update(self, window_width, window_height):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.lifetime -= 1

        if self.rect.left <= 0 or self.rect.right >= window_width:
            self.speed_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= window_height:
            self.speed_y *= -1

    def is_dead(self):
        return self.lifetime <= 0

class TargetManager:
    def __init__(self):
        self.targets = []
        self.spawn_timer = 0

    def spawn(self, window_width, window_height):
        self.spawn_timer -= 1

        if len(self.targets) < MAX_TARGETS and self.spawn_timer <= 0:
            size = random.randint(75, 175)
            speed_x = random.choice([-2, 0, 2])
            speed_y = random.choice([-2, 0, 2])

            x = random.randint(size, window_width - size)
            y = random.randint(size, window_height - size)

            self.targets.append(Target(x, y, size, size, speed_x, speed_y))
            self.spawn_timer = random.randint(30, 90)

    def update(self, window_width, window_height):
        for target in self.targets[:]:
            target.update(window_width, window_height)
        self.targets = [t for t in self.targets if not t.is_dead()]

    def check_click(self, mouse_pos):
        for target in self.targets[:]:
            if target.rect.collidepoint(mouse_pos):
                self.targets.remove(target)
                return target
        return None

class AimEnv:
    def __init__(self, render=False):
        self.render_mode = render
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT

        if self.render_mode:
            pygame.init()
            pygame.display.set_caption("Treino IA - Aim")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 24)

        self.action_space = 5
        self.observation_space = 14
        self.reset()

    def reset(self):
        self.tmanager = TargetManager()
        self.score = 0
        self.timer = 60 * 30
        self.done = False

        self.cursor_x = self.window_width / 2
        self.cursor_y = self.window_height / 2

        self.tmanager.spawn_timer = 0
        for _ in range(MAX_TARGETS):
            self.tmanager.spawn(self.window_width, self.window_height)

        return self.get_state()

    def get_state(self):
        state = [
            self.cursor_x / self.window_width,
            self.cursor_y / self.window_height
        ]

        for i in range(MAX_TARGETS):
            if i < len(self.tmanager.targets):
                t = self.tmanager.targets[i]
                state.extend([
                    t.rect.centerx / self.window_width,
                    t.rect.centery / self.window_height,
                    t.rect.width / 200,
                    t.lifetime / t.max_lifetime
                ])
            else:
                state.extend([0.0, 0.0, 0.0, 0.0])

        return state

    def step(self, action):
        reward = 0
        self.timer -= 1

        dist_old = float("inf")
        if self.tmanager.targets:
            nearest = min(self.tmanager.targets, key=lambda t: math.hypot(self.cursor_x - t.rect.centerx, self.cursor_y - t.rect.centery))
            dist_old = math.hypot(self.cursor_x - nearest.rect.centerx, self.cursor_y - nearest.rect.centery)

        if action == 0:
            self.cursor_y = max(0, self.cursor_y - CURSOR_SPEED)
        elif action == 1:
            self.cursor_y = min(self.window_height, self.cursor_y + CURSOR_SPEED)
        elif action == 2:
            self.cursor_x = max(0, self.cursor_x - CURSOR_SPEED)
        elif action == 3:
            self.cursor_x = min(self.window_width, self.cursor_x + CURSOR_SPEED)

        clicked = (action == 4)

        self.tmanager.spawn(self.window_width, self.window_height)
        self.tmanager.update(self.window_width, self.window_height)

        dist_new = float("inf")
        if self.tmanager.targets:
            nearest = min(self.tmanager.targets, key=lambda t: math.hypot(self.cursor_x - t.rect.centerx, self.cursor_y - t.rect.centery))
            dist_new = math.hypot(self.cursor_x - nearest.rect.centerx, self.cursor_y - nearest.rect.centery)

        if clicked:
            hit = self.tmanager.check_click((self.cursor_x, self.cursor_y))
            if hit:
                if hit.lifetime > 120:
                    reward += 5.0
                    self.score += 1
                else:
                    reward += 10.0
                    self.score += 2
            else:
                reward -= 0.05
        else:
            if dist_new < dist_old:
                reward += 0.05
            elif dist_new > dist_old:
                reward -= 0.05
            reward -= 0.01

        if self.timer <= 0:
            self.done = True

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

        self.screen.fill((0, 0, 0))

        for t in self.tmanager.targets:
            color = (255, 215, 0) if t.lifetime < 120 else (255, 255, 255)
            pygame.draw.rect(self.screen, color, t.rect)
            
        pygame.draw.circle(self.screen, (255, 0, 0), (int(self.cursor_x), int(self.cursor_y)), 6)
        
        score_txt = self.font.render(f"Score: {self.score}", True, (255,255,255))
        time_txt = self.font.render(f"Time: {self.timer//60}", True, (255,255,255))
        self.screen.blit(score_txt, (10, 10))
        self.screen.blit(time_txt, (10, 40))

        pygame.display.flip()
        self.clock.tick(60)