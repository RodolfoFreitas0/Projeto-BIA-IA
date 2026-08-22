import torch
import torch.nn as nn
import torch.optim as optim
import random
import matplotlib.pyplot as plt
from collections import deque
from game_env import DodgeEnv
from model import DQN
import os

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo:", device)

env = DodgeEnv(render=False)
model = DQN().to(device)

if os.path.exists("dodge_model.pth"):
    model.load_state_dict(torch.load("dodge_model.pth", map_location=device))
    print("Modelo carregado!")

optimizer = optim.Adam(model.parameters(), lr=0.001)
memory = deque(maxlen=100000)

gamma = 0.99
epsilon = 1.0
epsilon_decay = 0.997
epsilon_min = 0.05
BATCH_SIZE = 128

def choose_action(state):
    if random.random() < epsilon:
        return random.randint(0, 4)

    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        return torch.argmax(model(s)).item()

def train_batch():
    if len(memory) < 3000:
        return

    batch = random.sample(memory, BATCH_SIZE)

    states = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=device)
    actions = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device)
    rewards = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=device)
    next_states = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=device)
    dones = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=device)

    q_values = model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

    with torch.no_grad():
        next_q = model(next_states).max(1)[0]
        target = rewards + gamma * next_q * (1 - dones)

    loss = nn.MSELoss()(q_values, target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

scores = []
plt.ion()
fig, ax = plt.subplots()

for episode in range(10000):
    state = env.reset()
    total_reward = 0

    while True:
        action = choose_action(state)
        next_state, reward, done = env.step(action)

        memory.append((state, action, reward, next_state, done))
        state = next_state
        total_reward += reward

        train_batch()

        if done:
            break

    epsilon = max(epsilon_min, epsilon * epsilon_decay)
    scores.append(total_reward)

    if episode % 100 == 0:
        torch.save(model.state_dict(), "dodge_model.pth")
        print("Modelo salvo!")

    ax.clear()
    ax.plot(scores)
    plt.pause(0.001)

    print(f"Ep {episode} | Score {total_reward:.1f} | Epsilon {epsilon:.3f}")

plt.ioff()
plt.show()
