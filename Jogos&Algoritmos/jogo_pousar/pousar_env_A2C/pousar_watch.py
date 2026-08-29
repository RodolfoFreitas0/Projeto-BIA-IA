import torch
import os
from pousar_env import LunarLanderEnv
from pousar_model import A2C

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_pousar"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "pousar_model_a2c.pth")

INPUT_SIZE = 10
OUTPUT_SIZE = 4

env = LunarLanderEnv(render=True)
model = A2C(INPUT_SIZE, OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")
else:
    print("Nenhum modelo salvo encontrado em", SAVE_PATH)

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
