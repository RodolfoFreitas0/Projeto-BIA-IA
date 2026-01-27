import pygame

class StartScreen:
    def __init__(self, screen, clock, title):
        self.screen = screen
        self.clock = clock
        self.title = title

        self.width, self.height = self.screen.get_size()

        self.font_title = pygame.font.SysFont("Monocraft", 80)
        self.font_button = pygame.font.SysFont("Monocraft", 40)

        self.play_rect = pygame.Rect(self.width//2 - 150, 360, 300, 80)
        self.quit_rect = pygame.Rect(self.width//2 - 150, 480, 300, 80)

    def draw(self):
        self.screen.fill((0, 0, 0))

        title_surf = self.font_title.render(self.title, True, "white")
        self.screen.blit(
            title_surf,
            title_surf.get_rect(center=(self.width//2, 220))
        )
        
        pygame.draw.rect(self.screen, "white", self.play_rect, 3)
        pygame.draw.rect(self.screen, "white", self.quit_rect, 3)

        play_text = self.font_button.render("PLAY", True, "white")
        quit_text = self.font_button.render("QUIT", True, "white")

        self.screen.blit(play_text, play_text.get_rect(center=self.play_rect.center))
        self.screen.blit(quit_text, quit_text.get_rect(center=self.quit_rect.center))

        pygame.display.update()

    def run(self):
        while True:
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.quit:
                    return "QUIT"
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_rect.collidepoint(event.pos):
                        return "PLAY"
                    if self.quit_rect.collidepoint(event.pos):
                        return "QUIT"
            
            self.clock.tick(60)