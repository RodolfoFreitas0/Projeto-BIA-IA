import pygame
import scripts.core.settings as settings

class HUD:
    def __init__(self, game):
        self.game = game
        self.font_small = pygame.font.SysFont("Sans", 10) 
        self.font_big = pygame.font.SysFont("Sans", 15)
    
    def draw_score(self, surf):
        if not settings.PYGAME_MODE:
            return
        
        minutos = self.game.score // 60
        segundos = self.game.score % 60

        score_text = self.font_small.render(f"{minutos:02} : {segundos:02}", False, "White")
        score_rect = score_text.get_rect()

        score_rect.center = (self.game.display_width // 2 + 20, 10)
        background_rect = score_rect.inflate(9, 2)

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (0, 75, 150), background_rect, 1)
        surf.blit(score_text, score_rect)
    
    def draw_hp(self, surf):
        if not settings.PYGAME_MODE:
            return
        
        hp_text = self.font_small.render(f"hp: {self.game.player.HP}", False, "White")
        hp_rect = hp_text.get_rect()

        hp_rect.center = (self.game.display_width // 2 - 20, 10)
        background_rect = hp_rect.inflate(6, 2)

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (0, 75, 150), background_rect, 1)
        surf.blit(hp_text, hp_rect)

    def draw_gameover(self, surf):
        if not settings.PYGAME_MODE:
            return
        
        gameover_text = self.font_big.render("GAME OVER!", False, "White")
        gameover_rect = gameover_text.get_rect()

        gameover_rect.center = (self.game.display_width // 2, self.game.display_height // 2)

        background_rect = gameover_rect.inflate(10, 10)

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (0, 75, 150), background_rect, 1)
        surf.blit(gameover_text, gameover_rect)

    def draw_highscore(self, surf):
        if not settings.PYGAME_MODE:
            return
        
        minutosH = self.game.highscore // 60
        segundosH = self.game.highscore % 60

        if minutosH == 0:
            text = f" Highscore: {segundosH:02} s "
        else:
            text = f" Highscore: {minutosH:02} : {segundosH:02} "

        highscore_text = self.font_small.render(text, False, "White")
        highscore_rect = highscore_text.get_rect()

        highscore_rect.center = (self.game.display_width // 2, self.game.display_height // 2 - 80)
        background_rect = highscore_rect.inflate(6, 2)

        pygame.draw.rect(surf, (0, 0, 0), background_rect)
        pygame.draw.rect(surf, (0, 75, 150), background_rect, 1)
        surf.blit(highscore_text, highscore_rect)
