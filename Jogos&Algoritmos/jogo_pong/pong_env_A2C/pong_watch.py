import torch
import os
from pong_env import PongEnv
from pong_model import A2C

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo: ", device)

BASE_DIR = "Models"
GAME_NAME = "jogo_pong"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)

SAVE_PATH_R = os.path.join(SAVE_DIR, "pong_model_a2c_R.pth")
SAVE_PATH_L = os.path.join(SAVE_DIR, "pong_model_a2c_L.pth")

os.makedirs(SAVE_DIR, exist_ok=True)

env = PongEnv(render=True, player=False)
model_R = A2C().to(device)
model_L = A2C().to(device)

if os.path.exists(SAVE_PATH_R) and os.path.exists(SAVE_PATH_L):
    model_R.load_state_dict(torch.load(SAVE_PATH_R, map_location=device))
    model_L.load_state_dict(torch.load(SAVE_PATH_L, map_location=device))

model_R.eval()
model_L.eval()

state_R, state_L = env.reset()

while True:
    with torch.no_grad():
        s_R = torch.tensor(state_R, dtype=torch.float32, device=device).unsqueeze(0)
        logits_R, _ = model_R(s_R)
        action_R = torch.argmax(logits_R).item()

        s_L = torch.tensor(state_L, dtype=torch.float32, device=device).unsqueeze(0)
        logits_L, _ = model_L(s_L)
        action_L = torch.argmax(logits_L).item()

    
    state_R, state_L, _, _, done = env.step(action_R, action_L)

    if done:
        state_R, state_L = env.reset()