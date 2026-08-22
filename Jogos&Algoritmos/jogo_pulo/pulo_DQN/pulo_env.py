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
        next_obs = None
        for obs in self.obs.obstacles:
            if obs.rect.x > self.player.rect.x:
                next_obs = obs
                break
        
        if next_obs:
            distance = (next_obs.rect.x - self.player.rect.x) / WIDTH
            width = next_obs.rect.width / 100
        else:
            distance = 1
            width = 0
        
        return [
            self.player.rect.y / HEIGHT,
            self.player.speed_y / 10,
            distance,
            width
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
            if not obstacle.passed and obstacle.rect.right < player.rect.left:
                obstacle.passed = True
                self.passed_reward += 10

            if obstacle.rect.colliderect(player.rect):
                self.collided = True

            obstacle.update()
        
        self.obstacles = [obs for obs in self.obstacles if not obs.is_out()]

    def render(self, surf):
        for obstacle in self.obstacles[:]:
            obstacle.render(surf)