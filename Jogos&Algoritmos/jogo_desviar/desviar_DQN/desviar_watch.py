import torch
import os
from desviar_env import DodgerEnv
from desviar_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_desviar"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
SAVE_PATH = os.path.join(SAVE_DIR, "desviar_model_DQN.pth")

env = DodgerEnv(render=True)

INPUT_SIZE = 24
OUTPUT_SIZE = 5

model = DQN(input_size=INPUT_SIZE, output_size=OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))

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