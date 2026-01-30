import pygame

TILESIZE = 40

LINHAS = 15
COLUNAS = 15

WINDOW_WIDTH = COLUNAS * TILESIZE
WINDOW_HEIGHT = LINHAS * TILESIZE 

SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("Consolas", int(WINDOW_WIDTH/20))

TITLE = "COBRA IA"