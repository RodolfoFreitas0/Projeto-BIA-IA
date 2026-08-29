import torch
import random
import os
from pulo_env import PuloEnv
from pulo_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_pulo"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "pulo_model_dqn.pth")

env = PuloEnv(render=True, player=False)

INPUT_SIZE = 7
OUTPUT_SIZE = 2

model = DQN(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    checkpoint = torch.load(SAVE_PATH, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
    else:
        model.load_state_dict(checkpoint)

model.eval()

state = env.reset()

while True:
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        q_values = model(s)
        action = torch.argmax(q_values).item()

    state, reward, done = env.step(action)

    if done:
        state = env.reset()