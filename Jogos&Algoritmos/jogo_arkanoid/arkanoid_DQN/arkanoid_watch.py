import os
import time
import torch
from arkanoid_env import ArkanoidEnv
from arkanoid_model import DQN 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_arkanoid"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "arkanoid_model_dqn.pth")

INPUT_SIZE = 45
OUTPUT_SIZE = 3

model = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    model.eval()
    print("Modelo carregado!")
else:
    print("Modelo nao encontrado.")

env = ArkanoidEnv(render=True)

def watch():
    for episode in range(10):
        state = env.reset()
        done = False
        total_reward = 0
        
        while not done:
            t_state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
            
            with torch.no_grad():
                action = model(t_state).argmax().item()
            
            state, reward, done = env.step(action)
            total_reward += reward
            
            time.sleep(0.015)
            
        print(f"Episodio {episode + 1} | Score: {env.score} | Recompensa: {total_reward:.1f}")

if __name__ == "__main__":
    watch()