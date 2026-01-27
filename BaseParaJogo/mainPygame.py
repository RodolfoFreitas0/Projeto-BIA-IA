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

    def render(self):
        SCREEN.fill(0, 0, 0)

    def run(self):
        pass
        

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