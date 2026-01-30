import pygame
import sys
import random

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption(TITLE)

class Game():
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.hud = HUD()

        for _ in range(3):
            self.food.spawn(self.free_spaces())

        self.game_over = False
        self.timer = 10
        self.score = 0

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.snake.set_dir((0, -1))
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.snake.set_dir((-1, 0))
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.snake.set_dir((0, 1))
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.snake.set_dir((1, 0))
                
                if self.game_over == True:
                    self.game_over = False
                    return
            
        return True
    
    def free_spaces(self):
        while True:
            pos = (
                random.randint(0, 14),
                random.randint(0, 14)
            )
            
            if pos not in self.snake.body and pos not in self.food.positions:
                return pos

    def update(self):
        self.timer -= 1
        self.score = len(self.snake.body) - 3

        head = self.snake.body[0]

        if self.timer == 0:
            if self.food.eat(head):
                self.snake.grow = True
                self.food.spawn(self.free_spaces())

            self.snake.move()

            if self.snake.wall_colision():
                self.game_over = True
            
            if self.snake.self_collision():
                self.game_over = True

            self.timer = 10

        self.snake.grow = False

    def render(self, surf):
        SCREEN.fill((0, 0, 0))
        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

        self.food.render(surf)
        self.snake.render(surf)
        self.snake.render(surf)

        self.hud.draw_score(surf, self.score)

        pygame.draw.rect(surf, (255, 255, 255), screen_rect, 4)

    def run(self):
        running = True

        while running:
            events = pygame.event.get()

            running = self.handle_events(events)

            if self.game_over == False:
                self.update()
                self.render(SCREEN)
            else:
                self.hud.final_screen(SCREEN, self.score)

            pygame.display.update()
            CLOCK.tick(60)

class Snake():
    def __init__(self):

        self.body = [(7, 7), (6, 7), (5, 7)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.grow = False

    def move(self):
        self.direction = self.next_direction

        move = (
            self.body[0][0] + self.direction[0],
            self.body[0][1] + self.direction[1]
        )
        
        if self.grow:
            self.body.insert(0, move)
        else:
            self.body.pop()
            self.body.insert(0, move)
        
    def set_dir(self, new_dir):
        if self.direction[0] + new_dir[0] == 0 and \
            self.direction[1] + new_dir[1] == 0:
            return

        self.next_direction = new_dir

    def wall_colision(self):
        x = self.body[0][0]
        y = self.body[0][1]
        return x < 0 or x >= COLUNAS or y < 0 or y >= LINHAS
    
    def self_collision(self):
        head = self.body[0]
        return head in self.body[1:]

    def render(self, surf):
        for x, y in self.body:
            px = x * TILESIZE
            py = y * TILESIZE

            rect = pygame.Rect(px, py, TILESIZE, TILESIZE)
            pygame.draw.rect(surf, (0, 200, 0), rect)

class Food():
    def __init__(self):
        self.positions = []

    def spawn(self, pos):     
        self.positions.append(pos)
    
    def eat(self, pos):
        if pos in self.positions:
            self.positions.remove(pos)
            return True
        return False

    def render(self, surf):
        for x, y in self.positions:
            px = x * TILESIZE
            py = y * TILESIZE

            rect = pygame.Rect(px, py, TILESIZE, TILESIZE)
            pygame.draw.rect(surf, (200, 0, 0), rect)

class HUD():
    def __init__(self):
        self.font_big = pygame.font.SysFont("Monocraft", 40) 
        self.font_small = pygame.font.SysFont("Monocraft", 20)

    def draw_score(self, surf, score):
        score_text = self.font_big.render(f"{score:02}", False, "white")
        text_rect = score_text.get_rect()

        background_rect = text_rect.inflate(20, 20)
        background_rect.topleft = (15, 15)

        text_rect.centerx = background_rect.centerx + 2
        text_rect.centery = background_rect.centery

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (255, 255, 255), background_rect, 3)
        surf.blit(score_text, text_rect)

    def final_screen(self, surf, score):
        SCREEN.fill((0, 0, 0))

        text = self.font_big.render(f"Pontuação: |{score}|", True, "white")
        surf.blit(text, text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50)))

        info = self.font_small.render(f"Aperte qualquer tecla para voltar ao menu", True, "white")
        surf.blit(info, info.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50)))

if __name__ == "__main__":


    while True:
        start = StartScreen(SCREEN, CLOCK, TITLE)
        result = start.run()

        if result == "PLAY":
            game = Game()
            game.run()
        else:
            break
        
    pygame.quit()
    sys.exit()
    