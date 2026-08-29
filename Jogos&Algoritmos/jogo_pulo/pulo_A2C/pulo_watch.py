import torch
import os
from pulo_env import PuloEnv
from pulo_model import A2C

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_pulo"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "pulo_model_a2c.pth")

env = PuloEnv(render=True)
INPUT_SIZE = 7
OUTPUT_SIZE = 2

model = A2C(INPUT_SIZE, OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")

model.eval()

state = env.reset()

while True:
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        logits, val = model(s)
        action = torch.argmax(logits).item()

    state, reward, done = env.step(action)

    if done:
        state = env.reset()