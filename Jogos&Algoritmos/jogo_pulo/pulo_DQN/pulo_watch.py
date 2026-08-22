import torch
import random
from pulo_env import PuloEnv
from pulo_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = PuloEnv(render=True, player=True)
model = DQN().to(device)

model.load_state_dict(torch.load("pulo_model.pth", map_location=device))
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