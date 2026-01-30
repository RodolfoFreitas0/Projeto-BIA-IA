import pygame

from settings import *

class GameOver:
    def __init__(self, score, highscore):
        self.score = score
        self.highscore = highscore

        self.font_big = pygame.font.SysFont("Monocraft", 80)
        self.font_mid = pygame.font.SysFont("Monocraft", 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "RESTART"
                if event.key == pygame.K_m:
                    return "MENU"

        return None

    def render(self):
        SCREEN.fill((0, 0, 0))

        # Título
        title = self.font_big.render("GAME OVER", False, "white")
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 150))

        titleback_rect = title_rect.inflate(20, 20)

        pygame.draw.rect(SCREEN, (255, 255, 255), titleback_rect, 3)
        SCREEN.blit(title, title_rect)

        # Score
        score_text = self.font_mid.render(f"Score: {self.score}", False, "white")
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, 280))

        scoreback_rect = score_rect.inflate(20, 20)

        pygame.draw.rect(SCREEN, (255, 255, 255), scoreback_rect, 3)
        SCREEN.blit(score_text, score_rect)

        # Highscore
        hs_text = self.font_mid.render(f"Highscore: {self.highscore}", False, "white")
        hs_rect = hs_text.get_rect(center=(WINDOW_WIDTH//2, 360))

        highback_rect = hs_rect.inflate(20, 20)

        pygame.draw.rect(SCREEN, (255, 255, 255), highback_rect, 3)
        SCREEN.blit(hs_text, hs_rect)

        # Instruções
        info = self.font_mid.render("R - Recomeçar  |   M - Menu", False, "white")
        info_rect = info.get_rect(center=(WINDOW_WIDTH//2, 500))

        infoback_rect = info_rect.inflate(25, 25)

        pygame.draw.rect(SCREEN, (255, 255, 255), infoback_rect, 3)
        SCREEN.blit(info, info_rect)

        pygame.display.update()

    def run(self):
        while True:
            events = pygame.event.get()
            action = self.handle_events(events)

            if action:
                return action

            self.render()
            CLOCK.tick(60)