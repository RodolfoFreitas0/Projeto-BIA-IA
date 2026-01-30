import torch
from game_env import DodgeEnv
from model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = DodgeEnv(render=True)
model = DQN().to(device)
model.load_state_dict(torch.load("dodge_model.pth", map_location=device))
model.eval()

state = env.reset()

while True:
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        action = torch.argmax(model(s)).item()

    state, _, done = env.step(action)

    if done:
        state = env.reset()
