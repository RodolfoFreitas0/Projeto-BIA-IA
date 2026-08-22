import pygame
import csv
import os
import time
from cobrinha_env import CobraEnv

DATA = "Dados Humanos"
DATA_NAME = "dados_humano_cobrinha.csv"
DATA_ARCHIVE = os.path.join(DATA, DATA_NAME)

def save_data(episode, score, steps):
    if not os.path.exists(DATA):
        os.makedirs(DATA)

    arquivo_existe = os.path.isfile(DATA_ARCHIVE)
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not arquivo_existe:
            writer.writerow(["Episodio", "Score", "Passos"])
        writer.writerow([episode, score, steps])

def play_human():
    env = CobraEnv(render=True)
    episode = 1

    print(f"Os dados serao salvos em: {DATA_ARCHIVE}")
    print("Feche a janela para sair.\n")

    while True:
        env.reset()
        done = False
        steps = 0
        
        while not done:
            action = 0 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        action = 1
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        action = 2

            next_state, reward, done = env.step(action)
            steps += 1

        score = env.score
        print(f"Ep {episode} | Score: {score} | Steps: {steps} frames")
        
        save_data(episode, score, steps)
        episode += 1
        
        time.sleep(1) 

if __name__ == "__main__":
    play_human()