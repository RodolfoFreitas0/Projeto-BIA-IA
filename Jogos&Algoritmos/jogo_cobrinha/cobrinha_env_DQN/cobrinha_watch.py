import os
import torch
from cobrinha_model import DQN
from cobrinha_env import CobraEnv


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo: ", device)

env = CobraEnv(render=True)

BASE_DIR = "Models"
GAME_NAME = "jogo_cobrinha"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "cobrinha_model_dqn_2.pth")

input_size = 11

model = DQN(input_size).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")

model.eval()

state = env.reset()

while True:
    with torch.no_grad():
        s_tensor = torch.tensor(state, dtype=torch.float32, device=device)
        q_values = model(s_tensor)
        action = torch.argmax(q_values).item()

    state, reward, done = env.step(action)

    if done:
        state = env.reset()