import torch
from pong_env import PongEnv
from pong_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

env = PongEnv(render=True)
model = DQN().to(device)
model.load_state_dict(torch.load("pong_model(ModeloPerfeito).pth", map_location=device))
model.eval()

state = env.reset()

while True:
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        action = torch.argmax(model(s)).item()
    
    state, _, done = env.step(action)

    if done:
        state = env.reset()