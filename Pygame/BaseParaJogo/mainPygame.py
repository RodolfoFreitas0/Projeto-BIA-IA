import pygame
import sys

pygame.init()

from settings import *
from start_screen import StartScreen

pygame.display.set_caption(TITLE)

class Game():
    def __init__(self):
        pass

    def update(self):
        pass

    def render(self, surf):
        SCREEN.fill((0, 0, 0))
        screen_rect = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(surf, (255, 255, 255), screen_rect, 4)

    def run(self):
        
        while True:
            self.render(SCREEN)

            pygame.display.update()
            CLOCK.tick(60)

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