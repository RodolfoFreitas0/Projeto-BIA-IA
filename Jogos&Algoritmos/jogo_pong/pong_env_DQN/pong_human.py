import pygame
import csv
import os
import time
from pong_env import PongEnv

DATA = "Dados Humanos"
DATA_NAME = "dados_humano_pong.csv"
DATA_ARCHIVE = os.path.join(DATA, DATA_NAME)

def save_data(rally, human_score, bot_score, steps):
    if not os.path.exists(DATA):
        os.makedirs(DATA)

    arquivo_existe = os.path.isfile(DATA_ARCHIVE)
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not arquivo_existe:
            writer.writerow(["Rally", "Score Humano", "Score Bot", "Passos"])
        writer.writerow([rally, human_score, bot_score, steps])

def play_human():
    env = PongEnv(render=True, player=False)
    rally = 1

    print(f"Os dados serao salvos em: {DATA_ARCHIVE}")
    print("Controles: Setas Cima/Baixo para controlar a raquete da DIREITA.")
    print("Feche a janela para sair.\n")

    human_total = 0
    bot_total = 0

    while True:
        env.reset()
        
        env.AI_score = human_total % 10
        env.player_score = bot_total % 10
        
        done = False
        steps = 0
        
        while not done:
            action = 0 
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                action = 1
            elif keys[pygame.K_DOWN]:
                action = 2

            next_state, reward, done = env.step(action)
            steps += 1

        if env.ball.left < 0:
            human_total += 1
            vencedor = "Humano"
        else:
            bot_total += 1
            vencedor = "Bot"

        print(f"Rally {rally} | Venceu: {vencedor} | Placar: Humano {human_total} x {bot_total} Bot | Steps: {steps} frames")
        
        save_data(rally, human_total, bot_total, steps)
        rally += 1
        
        time.sleep(1) 

if __name__ == "__main__":
    play_human() 