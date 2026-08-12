import torch
import os
from passaro_env import FlappyEnv
from passaro_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo:", device)

BASE_DIR = "Models"
GAME_NAME = "jogo_passaro"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "passaro_model_DQN.pth")

env = FlappyEnv(render=True)

INPUT_SIZE = 5
OUTPUT_SIZE = 2
model = DQN(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")

model.eval()

state = env.reset()

while True:
    with torch.no_grad():
        s_tensor = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        q_values = model(s_tensor)
        action = torch.argmax(q_values).item()
    
    state, reward, done = env.step(action)

    if done:
        state = env.reset()