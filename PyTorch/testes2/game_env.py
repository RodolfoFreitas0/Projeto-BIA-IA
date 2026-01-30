import pygame
import random

WIDTH, HEIGHT = 800, 600

class DodgeEnv:
    def __init__(self, render=False):
        self.render_mode = render

        if render:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            pygame.display.set_caption("IA Jogando")
            self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        self.player = pygame.Rect(WIDTH//2, HEIGHT-80, 40, 40)
        self.enemies = []
        self.spawn_timer = 0
        self.enemy_speed = 6
        self.done = False
        self.score = 0
        return self.get_state()

    def spawn_enemy(self):
        x = random.randint(0, WIDTH-40)
        self.enemies.append(pygame.Rect(x, -40, 40, 40))

    def step(self, action):
        # ações
        if action == 1: self.player.x -= 7
        if action == 2: self.player.x += 7
        if action == 3: self.player.y -= 7
        if action == 4: self.player.y += 7

        self.player.clamp_ip(pygame.Rect(0,0,WIDTH,HEIGHT))

        # spawn
        self.spawn_timer += 1
        if self.spawn_timer > 25:
            self.spawn_timer = 0
            self.spawn_enemy()

        reward = -0.01  # punição por ficar parado
        player_y = self.player.y

        for enemy in self.enemies[:]:
            enemy.y += self.enemy_speed

            # DESVIOU do inimigo (passou perto e não colidiu)
            if enemy.y > player_y and abs(enemy.x - self.player.x) < 50:
                reward += 5

            if enemy.y > HEIGHT:
                self.enemies.remove(enemy)
                self.score += 1
                reward += 2

            if enemy.colliderect(self.player):
                self.done = True
                reward = -50

        if self.render_mode:
            self.render()

        return self.get_state(), reward, self.done

    # --------------------------------------------------
    # NOVO STATE (muito melhor)
    # --------------------------------------------------
    def get_state(self):
        nearest = min(self.enemies, key=lambda e: e.y, default=None)

        if nearest:
            return [
                self.player.x / WIDTH,
                self.player.y / HEIGHT,
                nearest.x / WIDTH,
                nearest.y / HEIGHT,
                (nearest.x - self.player.x) / WIDTH,
                (nearest.y - self.player.y) / HEIGHT,
            ]
        else:
            return [0,0,0,0,0,0]

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        self.screen.fill((255, 255, 255))
        pygame.draw.rect(self.screen, (50,150,255), self.player)

        for e in self.enemies:
            pygame.draw.rect(self.screen, (200,50,50), e)

        pygame.display.flip()
        self.clock.tick(60)
