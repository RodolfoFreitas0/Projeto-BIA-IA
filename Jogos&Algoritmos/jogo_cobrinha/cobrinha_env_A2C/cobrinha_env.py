import random
import math
import sys

try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False

TILESIZE = 40

LINHAS = 15
COLUNAS = 15

WIDTH = COLUNAS * TILESIZE
HEIGHT = LINHAS * TILESIZE

class CobraEnv:
    def __init__(self, render=False):
        self.render_mode = render
        self.snake = None
        self.food = None
        self.score = 0
        self.steps_taken = 0
        self.max_steps_per_ep = COLUNAS * LINHAS * 2
        self.target_food = None

        if self.render_mode and not pygame_available:
            print("Instale o pygame")
            self.render_mode = False
        
        if self.render_mode:
            pygame.init()
            pygame.display.set_caption("Treino IA")
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.Clock()
        
        self.action_space = 3
        self.obs_space_shape = (LINHAS, COLUNAS)
        self.reset()

    def reset(self):
        self.snake = Snake(LINHAS, COLUNAS)
        self.food = Food()
        self.score = 0
        self.steps_taken = 0
        self.done = False
        self.target_food = None

        for _ in range(3):
            self.food.spawn(self.free_spaces())

        head_x, head_y = self.snake.head
        dist_max = -1
        for fx, fy in self.food.positions:
            dist = math.sqrt((head_x - fx)**2 + (head_y - fy)**2)
            if dist > dist_max:
                dist_max = dist
                self.target_food = (fx, fy)

        return self.get_state()

    def is_collision(self, pt):
        if pt[0] < 0 or pt[0] >= COLUNAS or pt[1] < 0 or pt[1] >= LINHAS:
            return True
        if pt in self.snake.body[1:]:
            return True
        return False
    
    def get_state(self):
        head = self.snake.head
        point_l = (head[0] - 1, head[1])
        point_r = (head[0] + 1, head[1])
        point_u = (head[0], head[1] - 1)
        point_d = (head[0], head[1] + 1)

        dir_l = self.snake.direction == (-1, 0)
        dir_r = self.snake.direction == (1, 0)
        dir_u = self.snake.direction == (0, -1)
        dir_d = self.snake.direction == (0, 1)

        target = self.target_food if self.target_food else head

        state = [
            # Checa se o ponto na frente é seguro
            (dir_r and self.is_collision(point_r)) or
            (dir_l and self.is_collision(point_l)) or
            (dir_u and self.is_collision(point_u)) or
            (dir_d and self.is_collision(point_d)),

            # Checa se o ponto a direita é seguro
            (dir_r and self.is_collision(point_d)) or
            (dir_l and self.is_collision(point_u)) or
            (dir_u and self.is_collision(point_r)) or
            (dir_d and self.is_collision(point_l)),

            # Checa se o ponto a esquerda é seguro
            (dir_r and self.is_collision(point_u)) or
            (dir_l and self.is_collision(point_d)) or
            (dir_u and self.is_collision(point_l)) or
            (dir_d and self.is_collision(point_r)),

            # Direção Atual
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Localização da comida1
            target[0] < head[0],
            target[0] > head[0],
            target[1] < head[1],
            target[1] > head[1],
        ]

        return [int(x) for x in state]
    
    def free_spaces(self):
        while True:
            pos = (
                random.randint(0, 14),
                random.randint(0, 14)
            )

            if pos not in self.snake.body and pos not in self.food.positions:
                return pos

    def step(self, action):
        reward = 0
        self.steps_taken += 1
        head_x, head_y = self.snake.head

        if self.target_food not in self.food.positions:
            if self.food.positions:
                dist_max = -1
                for fx, fy in self.food.positions:
                    dist = math.sqrt((head_x - fx)**2 + (head_y - fy)**2)
                    if dist > dist_max:
                        dist_max = dist
                        self.target_food = (fx, fy)
            else:
                self.target_food = self.snake.head

        dist_old = math.sqrt((head_x - self.target_food[0])**2 + (head_y - self.target_food[1])**2)

        self.snake.set_dir(action)
        self.snake.move()

        new_head_x, new_head_y = self.snake.head
        dist_new = math.sqrt((new_head_x - self.target_food[0])**2 + (new_head_y - self.target_food[1])**2)

        if self.snake.wall_collision() or self.snake.self_collision():
            self.done = True
            reward -= 1
            return self.get_state(), reward, self.done
        
        if self.food.eat(self.snake.head):
            self.snake.grow = True
            self.score += 1
            reward += 1
            self.steps_taken = 0
            self.food.spawn(self.free_spaces())
        else:
            self.snake.grow = False

            if dist_new < dist_old:
                reward += 0.1
            else:
                reward -= 0.15

            if action != 0:
                reward -= 0.01

            reward -= 0.01
        
        if self.steps_taken > self.max_steps_per_ep:
            self.done = True
            reward -= 5
            
        if self.render_mode:
            self.render()
        
        return self.get_state(), reward, self.done
    
    def render(self):
        if not self.render_mode or not pygame_available:
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        self.screen.fill((0,0,0))
        screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)

        for x, y in self.snake.body:
            px = x * TILESIZE
            py = y * TILESIZE

            rect = pygame.Rect(px, py, TILESIZE, TILESIZE)
            pygame.draw.rect(self.screen, (0, 200, 0), rect)
        
        for x, y in self.food.positions:
            px = x * TILESIZE
            py = y * TILESIZE

            rect = pygame.Rect(px, py, TILESIZE, TILESIZE)
            pygame.draw.rect(self.screen, (200, 0, 0), rect)

        if self.target_food in self.food.positions:
            tx = self.target_food[0] * TILESIZE
            ty = self.target_food[1] * TILESIZE

            target_rect = pygame.Rect(tx + 10, ty + 10, TILESIZE - 20, TILESIZE - 20)
            pygame.draw.rect(self.screen, (255, 255, 255), target_rect)
        
        pygame.display.flip()
        self.clock.tick(10)

        pygame.draw.rect(self.screen, (255, 255, 255), screen_rect, 4)


class Snake:
    def __init__(self, grid_width, grid_height):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.body = [
            (self.grid_width // 2, self.grid_height // 2),
            (self.grid_width // 2 - 1, self.grid_height // 2),
            (self.grid_width // 2 - 2, self.grid_height // 2)
        ]
        self.head = self.body[0]
        self.direction = (1, 0)
        self.grow = False
    
    def move(self):
        if self.grow:
            self.body.insert(0, (self.head[0] + self.direction[0], self.head[1] + self.direction[1]))
        else:
            self.body.pop()
            self.body.insert(0, (self.head[0] + self.direction[0], self.head[1] + self.direction[1]))
        self.head = self.body[0]
    
    def set_dir(self, action):
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]

        cur_dir = dirs.index(self.direction)

        if action == 0:
            new_dir = dirs[cur_dir]
        elif action == 1:
            new_dir = dirs[(cur_dir + 1) % 4]
        elif action == 2:
            new_dir = dirs[(cur_dir - 1) % 4]

        self.direction = new_dir
    
    def wall_collision(self):
        x = self.head[0]
        y = self.head[1]
        return x < 0 or x >= COLUNAS or y < 0 or y >= LINHAS
    
    def self_collision(self):
        return self.head in self.body[1:]

class Food:
    def __init__(self):
        self.positions = []
    
    def spawn(self, pos):
        self.positions.append(pos)
    
    def eat(self, pos):
        if pos in self.positions:
            self.positions.remove(pos)
            return True
        return False