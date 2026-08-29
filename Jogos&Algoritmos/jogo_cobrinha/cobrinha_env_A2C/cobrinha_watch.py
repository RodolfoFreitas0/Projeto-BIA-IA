import torch
import os
from cobrinha_env import CobraEnv
from cobrinha_model import A2C

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo: ", device)

BASE_DIR = "Models"
GAME_NAME = "jogo_cobrinha"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "cobrinha_model_a2c.pth")

env = CobraEnv(render=True)

INPUT_SIZE = 11
OUTPUT_SIZE = 3
model = A2C(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")

model.eval()
state = env.reset()

while True:
    with torch.no_grad():
        s_tensor = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        logits, _ = model(s_tensor)

        action = torch.argmax(logits).item()

    state, reward, done = env.step(action)

    if done:
        state = env.reset()