import pygame

import scripts.core.settings as settings

pygame.init()
font = pygame.font.Font(None, 12)

def Debug(info, x = 10, y = 10, surf=None):
    if not settings.PYGAME_MODE:
            return
        
    if surf == None:
        surf = pygame.display.get_surface()
    debug_surf = font.render(str(info), True, "White")
    debug_rect = debug_surf.get_rect(topleft=(x,y))
    pygame.draw.rect(surf,"Black",debug_rect)
    surf.blit(debug_surf, debug_rect)