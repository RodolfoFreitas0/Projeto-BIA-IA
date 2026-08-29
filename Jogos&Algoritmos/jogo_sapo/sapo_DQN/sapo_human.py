import pygame
import csv
import os
import time
from sapo_env import FroggerEnv

DATA = "Dados Humanos"
DATA_NAME = "dados_humano_sapo.csv"
DATA_ARCHIVE = os.path.join(DATA, DATA_NAME)

def save_data(episode, steps):
    if not os.path.exists(DATA):
        os.makedirs(DATA)

    arquivo_existe = os.path.isfile(DATA_ARCHIVE)
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not arquivo_existe:
            writer.writerow(["Episodio", "Passos"])
        writer.writerow([episode, steps])

def play_human():
    env = FroggerEnv(render=True)
    episode = 1

    print(f"Os dados serao salvos em: {DATA_ARCHIVE}")
    print("Controles: Setas para mover o sapo.")
    print("Feche a janela para sair.\n")

    while True:
        env.reset()
        done = False
        steps = 0
        
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            keys = pygame.key.get_pressed()
            action = 0
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                action = 1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                action = 2
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                action = 3
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                action = 4

            next_state, reward, done = env.step(action)
            steps += 1

        print(f"Ep {episode} | Steps: {steps} frames")
        
        save_data(episode, steps)
        episode += 1
        
        time.sleep(1) 

if __name__ == "__main__":
    play_human()