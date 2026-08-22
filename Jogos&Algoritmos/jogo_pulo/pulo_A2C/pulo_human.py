import pygame
import csv
import os
import time
from pulo_env import PuloEnv

DATA = "Dados Humanos"
DATA_NAME = "dados_humano_pulo.csv"
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
    env = PuloEnv(render=True, player=True)
    episode = 1

    print(f"Os dados serao salvos em: {DATA_ARCHIVE}")
    print("Controles: Barra de espaco ou Seta para Cima para pular.")
    print("Feche a janela para sair.\n")

    while True:
        env.reset()
        done = False
        steps = 0
        total_reward = 0
        
        while not done:
            action = 0 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        action = 1

            next_state, reward, done = env.step(action)
            total_reward += reward
            steps += 1

        print(f"Ep {episode} | Score (Reward): {total_reward:.1f} | Steps: {steps} frames")
        
        save_data(episode, total_reward, steps)
        episode += 1
        
        time.sleep(1) 

if __name__ == "__main__":
    play_human()