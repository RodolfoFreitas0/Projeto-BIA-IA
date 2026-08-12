import pygame

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("Consolas", int(WINDOW_WIDTH/20))

TITLE = "FLAPPY AI"