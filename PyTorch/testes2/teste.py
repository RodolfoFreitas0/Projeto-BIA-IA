import pygame
import random
import sys

# Inicialização
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desvie dos Quadrados")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

# Cores
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (200, 50, 50)

# Jogador
player_size = 40
player = pygame.Rect(WIDTH // 2, HEIGHT - 80, player_size, player_size)
player_speed = 5

# Inimigos
enemy_size = 40
enemies = []
enemy_speed = 5
spawn_timer = 0

# Pontuação
score = 0

# Loop principal
running = True
while running:
    clock.tick(60)
    screen.fill(WHITE)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movimento do jogador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_UP]:
        player.y -= player_speed
    if keys[pygame.K_DOWN]:
        player.y += player_speed

    # Limites da tela
    player.clamp_ip(screen.get_rect())

    # Criar inimigos
    spawn_timer += 1
    if spawn_timer > 30:
        spawn_timer = 0
        x = random.randint(0, WIDTH - enemy_size)
        enemies.append(pygame.Rect(x, -enemy_size, enemy_size, enemy_size))

    # Atualizar inimigos
    for enemy in enemies[:]:
        enemy.y += enemy_speed
        if enemy.y > HEIGHT:
            enemies.remove(enemy)
            score += 1

        # Colisão
        if enemy.colliderect(player):
            running = False

    # Desenhar
    pygame.draw.rect(screen, BLUE, player)
    for enemy in enemies:
        pygame.draw.rect(screen, RED, enemy)

    # Texto de pontuação
    text = font.render(f"Pontos: {score}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()

# Game Over
screen.fill(WHITE)
game_over_text = font.render("Game Over", True, (0, 0, 0))
score_text = font.render(f"Pontuação final: {score}", True, (0, 0, 0))
screen.blit(game_over_text, (WIDTH // 2 - 80, HEIGHT // 2 - 40))
screen.blit(score_text, (WIDTH // 2 - 120, HEIGHT // 2))
pygame.display.flip()

pygame.time.delay(3000)
pygame.quit()
sys.exit()