import os
import torch
import random
import csv
import torch.nn as nn
import torch.optim as optim
from collections import deque
from pulo_model import DQN
from pulo_env import PuloEnv

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Device: ", device)

env = PuloEnv(render=False)

BASE_DIR = "Models"
GAME_NAME = "jogo_pulo"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "pulo_model_dqn.pth")

DATA_DIR = "Dados IA"
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_pulo.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Score", "Passos"])

model = DQN().to(device)
target_model = DQN().to(device)
target_model.load_state_dict(model.state_dict())
target_model.eval()

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    target_model.load_state_dict(model.state_dict())
    print("Modelo carregado!")

optimizer = optim.Adam(model.parameters(), lr=0.001)
memory = deque(maxlen=5000)

gamma = 0.99
epsilon = 1.0
epsilon_decay = 0.997
epsilon_min = 0.01
BATCH_SIZE = 64

def choose_action(state):
    if random.random() < epsilon:
        return random.randint(0, 1)
    
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        q_values = model(s)
        return torch.argmax(q_values).item()

def train_batch():
    if len(memory) < BATCH_SIZE:
        return
    
    batch = random.sample(memory, BATCH_SIZE)

    states = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=device)
    actions = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device)
    rewards = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=device)
    next_states = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=device)
    dones = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=device)

    q_values = model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

    with torch.no_grad():
        next_q = target_model(next_states).max(1)[0]
        target = rewards + gamma * next_q * (1 - dones)
        target = target.detach()

    loss = nn.MSELoss()(q_values, target)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

def save_data(episode, score, steps):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([episode, score, steps])

scores = []
total_steps = 0

for episode in range(10001):
    state = env.reset()
    total_reward = 0
    steps = 0

    while True:
        total_steps += 1
        steps += 1
        
        action = choose_action(state)
        next_state, reward, done = env.step(action)

        memory.append((state, action, reward, next_state, done))
        state = next_state
        total_reward += reward

        if total_steps % 4 == 0:
            train_batch()

        if total_steps % 1000 == 0:
            target_model.load_state_dict(model.state_dict())

        if done:
            break
    
    epsilon = max(epsilon_min, epsilon * epsilon_decay)
    scores.append(total_reward)
    
    save_data(episode, total_reward, steps)

    if episode % 100 == 0:
        torch.save(model.state_dict(), SAVE_PATH)
        print("Modelo Salvo!")

    if episode % 10 == 0:
        print(f"Ep {episode} | Score {total_reward:.1f} | Epsilon {epsilon:.3f}")