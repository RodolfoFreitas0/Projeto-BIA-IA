import pygame
import random
import sys

from setttings import *

pygame.init()
pygame.display.set_caption(TITLE)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.exit()
            sys.exit()

    pygame.display.update