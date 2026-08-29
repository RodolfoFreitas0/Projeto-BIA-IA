import torch
import os
from pong_env import PongEnv
from pong_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_pong"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)

MODEL_NAME_R = "pong_model_dqn_R.pth"
MODEL_NAME_L = "pong_model_dqn_L.pth"

SAVE_PATH_R = os.path.join(SAVE_DIR, MODEL_NAME_R)
SAVE_PATH_L = os.path.join(SAVE_DIR, MODEL_NAME_L)

PLAYER_MODE = False

env = PongEnv(render=True, player=PLAYER_MODE)

INPUT_SIZE = 7
OUTPUT_SIZE = 3

model_R = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
model_L = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device) if not PLAYER_MODE else None

def load_checkpoint(model, path):
    if os.path.exists(path):
        checkpoint = torch.load(path, map_location=device)
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        else:
            model.load_state_dict(checkpoint)
        print(f"Modelo carregado: {path}")
    else:
        print(f"Modelo não encontrado: {path}")

load_checkpoint(model_R, SAVE_PATH_R)
model_R.eval()

if not PLAYER_MODE:
    load_checkpoint(model_L, SAVE_PATH_L)
    model_L.eval()

if PLAYER_MODE:
    state_R = env.reset()
else:
    state_R, state_L = env.reset()

while True:
    with torch.no_grad():
        s_r = torch.tensor(state_R, dtype=torch.float32, device=device).unsqueeze(0)
        q_values_r = model_R(s_r)
        action_R = torch.argmax(q_values_r).item()
        
        if not PLAYER_MODE:
            s_l = torch.tensor(state_L, dtype=torch.float32, device=device).unsqueeze(0)
            q_values_l = model_L(s_l)
            action_L = torch.argmax(q_values_l).item()
        else:
            action_L = 0
    
    if PLAYER_MODE:
        state_R, reward_R, done = env.step(action_R)
    else:
        state_R, state_L, reward_R, reward_L, done = env.step(action_R, action_L)

    if done:
        if PLAYER_MODE:
            state_R = env.reset()
        else:
            state_R, state_L = env.reset()