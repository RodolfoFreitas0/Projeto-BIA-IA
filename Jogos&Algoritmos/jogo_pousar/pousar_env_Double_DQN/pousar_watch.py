import torch
import os
from pousar_env import LunarLanderEnv
from pousar_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_pousar"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "pousar_model_DQN.pth")

env = LunarLanderEnv(render=True)

INPUT_SIZE = 10
OUTPUT_SIZE = 4

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
        state_tensor = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        q_values = model(state_tensor)
        action = torch.argmax(q_values).item()
    
    state, reward, done = env.step(action)

    if done:
        state = env.reset()