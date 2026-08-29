import pygame
import random

WIDTH, HEIGHT = 800, 400

class PuloEnv:
    def __init__(self, render=False, player=False):
        self.render_mode = render
        self.player_mode = player

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
        
        self.reset()

    def reset(self):
        self.player = Player(50, HEIGHT // 2)

        self.obs = Obstacle_Manager(self)
        
        self.score = 0
        self.done = False
        self.steps = 0

        return self.get_state()

    def step(self, action):
        reward = 0
        self.steps += 1

        if action == 1 and self.player.on_ground:
            self.player.jump()
        elif action == 0:
            pass
        
        self.player.update()
        self.obs.update(self.player)

        reward += 0.1

        reward += self.obs.passed_reward
        self.obs.passed_reward = 0

        if self.obs.collided:
            reward -= 100
            self.done = True

        if self.steps > 2000:
            self.done = True

        if self.render_mode:
            self.render()

        return self.get_state(), reward, self.done

    def get_state(self):
        upcoming = sorted(
            (obs for obs in self.obs.obstacles if obs.rect.x > self.player.rect.x),
            key=lambda o: o.rect.x
        )

        def obs_features(obs):
            if obs is None:
                return 1.0, 0.0
            distance = (obs.rect.x - self.player.rect.x) / WIDTH
            width = obs.rect.width / 100
            return distance, width

        next_obs = upcoming[0] if len(upcoming) > 0 else None
        second_obs = upcoming[1] if len(upcoming) > 1 else None

        distance, width = obs_features(next_obs)
        distance2, width2 = obs_features(second_obs)

        obstacle_speed = (next_obs.speed_x / 10) if next_obs else 0.0

        return [
            self.player.rect.y / HEIGHT,
            self.player.speed_y / 10,
            distance,
            width,
            distance2,
            width2,
            obstacle_speed
        ]

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        self.screen.fill((0, 0, 0))

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (-40, HEIGHT // 2 + 62),
            (WIDTH + 40, HEIGHT // 2 + 62),
            5
        )

        pygame.draw.rect(self.screen, (255, 255, 255), self.player.rect)

        for obs in self.obs.obstacles:
            pygame.draw.rect(self.screen, (255, 255, 255), obs.rect)

        pygame.display.flip()
        self.clock.tick(60)

class Player():
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.speed_y = 0
        self.gravity = 0.65
        self.jump_force = -10
        self.on_ground = False
        self.ground_y = HEIGHT // 2 + 40
    
    def update(self):
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        if self.rect.y > self.ground_y:
            self.rect.y = self.ground_y
            self.speed_y = 0
            self.on_ground = True
        else:
            self.on_ground = False
    
    def jump(self):
        self.speed_y = self.jump_force

class Obstacle():
    def __init__(self):
        width = random.choice([2, 4, 6])
        self.rect = pygame.Rect(WIDTH + 30, HEIGHT // 2 + 40, width * 10, 20)
        self.speed_x = 5
        self.passed = False
        self.min_gap = None
    
    def is_out(self):
        return self.rect.x < -60

    def update(self):
        self.rect.x -= self.speed_x

    def render(self, surf):
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 0)

class Obstacle_Manager():
    def __init__(self, game):
        self.obstacles = []
        self.timer = 200
        self.game = game

        self.passed_reward = 0
        self.collided = False

    def spawn(self):
        self.obstacles.append(Obstacle())

    def update(self, player):
        self.collided = False
        self.timer -= 10

        if self.timer <= 0:
            self.spawn()
            self.timer = random.randint(300, 800)
    
        for obstacle in self.obstacles[:]:
            horizontally_overlapping = (
                obstacle.rect.right > player.rect.left and
                obstacle.rect.left < player.rect.right
            )

            if horizontally_overlapping and player.rect.bottom <= obstacle.rect.top:
                gap = obstacle.rect.top - player.rect.bottom
                if obstacle.min_gap is None or gap < obstacle.min_gap:
                    obstacle.min_gap = gap

            if not obstacle.passed and obstacle.rect.right < player.rect.left:
                obstacle.passed = True
                self.passed_reward += 10
                
                if obstacle.min_gap is not None:
                    clearance_bonus = max(0.0, min(obstacle.min_gap / 20, 1.0)) * 5
                    self.passed_reward += clearance_bonus

            if obstacle.rect.colliderect(player.rect):
                self.collided = True

            obstacle.update()
        
        self.obstacles = [obs for obs in self.obstacles if not obs.is_out()]

    def render(self, surf):
        for obstacle in self.obstacles[:]:
            obstacle.render(surf)