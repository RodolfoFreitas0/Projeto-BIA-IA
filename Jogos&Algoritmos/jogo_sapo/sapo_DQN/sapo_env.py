import pygame
import random
import sys

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class Frog:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.speed = 40
        self.timer = 0
        self.reset()
    
    def reset(self):
        start_x = random.randint(0, (WINDOW_WIDTH // 40) - 1) * 40
        self.rect = pygame.Rect(start_x, WINDOW_HEIGHT - 60, self.width, self.height)

    def move(self, dx, dy):
        self.timer += 1
        if self.timer >= 15:
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            self.rect.left = max(0, self.rect.left)
            self.rect.right = min(WINDOW_WIDTH, self.rect.right)
            self.rect.bottom = min(WINDOW_HEIGHT, self.rect.bottom)
            self.timer = 0

class Obstacle:
    def __init__(self, x, y, width, direction, delay):
        self.rect = pygame.Rect(x, y, width, 40)
        self.direction = direction
        self.delay = delay
        self.timer = 0

    def update(self):
        self.timer += 1
        if self.timer >= self.delay:
            self.rect.x += self.direction * 40
            self.timer = 0
            if self.direction > 0 and self.rect.left > WINDOW_WIDTH:
                self.rect.right = -(random.randint(1, 5) * 40)
            elif self.direction < 0 and self.rect.right < 0:
                self.rect.left = WINDOW_WIDTH + (random.randint(1, 5) * 40)

class FroggerEnv:
    def __init__(self, render=False):
        self.render_mode = render
        self.window_width = WINDOW_WIDTH
        self.window_height = WINDOW_HEIGHT
        
        if self.render_mode:
            pygame.init()
            pygame.display.set_caption("Treino IA - Frogger")
            self.screen = pygame.display.set_mode((self.window_width, self.window_height))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.SysFont("Arial", 24)
            
        self.action_space = 5
        self.observation_space = 17
        self.reset()

    def create_lanes(self):
        lanes_y = [100, 140, 180, 220, 260, 340, 380, 420, 460, 500]
        for y in lanes_y:
            direction = random.choice([-1, 1])
            for _ in range(random.randint(2, 4)):
                x = random.randint(0, (WINDOW_WIDTH // 40) - 1) * 40
                delay = 15
                width = random.choice([40, 80, 120])
                self.obstacles.append(Obstacle(x, y, width, direction, delay))

    def reset(self):
        self.frog = Frog()
        self.obstacles = []
        self.create_lanes()
        self.done = False
        self.steps = 0
        self.highest_y = self.frog.rect.y
        return self.get_state()

    def get_state(self):
        state = [
            self.frog.rect.x / WINDOW_WIDTH,
            self.frog.rect.y / WINDOW_HEIGHT
        ]
        
        for offset_y in [-40, 0, 40]:
            check_y = self.frog.rect.y + offset_y
            dist_left = 1.0
            dist_right = 1.0
            lane_speed = 0.0
            lane_timer = 0.0
            
            for obs in self.obstacles:
                if obs.rect.y == check_y:
                    lane_speed = obs.direction
                    lane_timer = obs.timer / obs.delay
                    if obs.rect.centerx < self.frog.rect.centerx:
                        d = max(0, (self.frog.rect.left - obs.rect.right)) / WINDOW_WIDTH
                        if d < dist_left:
                            dist_left = d
                    else:
                        d = max(0, (obs.rect.left - self.frog.rect.right)) / WINDOW_WIDTH
                        if d < dist_right:
                            dist_right = d
            
            state.extend([dist_left, dist_right, lane_speed, lane_timer])
        
        state.append(1.0 if self.frog.rect.left <= 0 else 0.0)
        state.append(1.0 if self.frog.rect.right >= WINDOW_WIDTH else 0.0)
        state.append(self.frog.rect.y / WINDOW_HEIGHT)
        
        return state

    def step(self, action):
        reward = -0.1
        self.steps += 1
        
        if action == 1:
            self.frog.move(0, -1)
        elif action == 2:
            self.frog.move(0, 1)
            reward -= 1.0
        elif action == 3:
            self.frog.move(-1, 0)
        elif action == 4:
            self.frog.move(1, 0)

        if self.frog.rect.y < self.highest_y:
            reward += 10.0
            self.highest_y = self.frog.rect.y

        for obs in self.obstacles:
            obs.update()
            
        for obs in self.obstacles:
            if self.frog.rect.colliderect(obs.rect):
                self.done = True
                reward -= 20.0
                break
                
        if not self.done and self.frog.rect.top <= 60:
            self.done = True
            reward += 100.0

        if self.steps > 1500:
            self.done = True
            reward -= 10.0

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
        
        safe_zones = [
            pygame.Rect(0, WINDOW_HEIGHT - 60, WINDOW_WIDTH, 300),
            pygame.Rect(0, 300, WINDOW_WIDTH, 40),
            pygame.Rect(0, 0, WINDOW_WIDTH, 100)
        ]
        for zone in safe_zones:
            pygame.draw.rect(self.screen, (20, 20, 20), zone)

        pygame.draw.rect(self.screen, (0, 255, 0), self.frog.rect)
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, (255, 0, 0), obs.rect)

        pygame.display.flip()
        self.clock.tick(60)