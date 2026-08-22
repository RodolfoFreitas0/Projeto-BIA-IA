import os
import csv
import random
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from arkanoid_env import ArkanoidEnv
from arkanoid_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_arkanoid"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "arkanoid_model_dqn.pth")

DATA_DIR = "Dados IA"
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_arkanoid_dqn.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Score", "Passos"])

INPUT_SIZE = 45
OUTPUT_SIZE = 3
GAMMA = 0.99
LR = 0.0005
BATCH_SIZE = 64
MEMORY_SIZE = 50000
MAX_EPISODES = 10000
TARGET_UPDATE = 10

epsilon = 1.0
epsilon_min = 0.05
epsilon_decay = 0.995

policy_net = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_net = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    policy_net.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    epsilon = epsilon_min

target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.Adam(policy_net.parameters(), lr=LR)
memory = deque(maxlen=MEMORY_SIZE)
env = ArkanoidEnv(render=False)

def save_data(episode, score, steps):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([episode, score, steps])

for episode in range(MAX_EPISODES):
    state = env.reset()
    total_reward = 0
    steps = 0
    done = False

    while not done:
        steps += 1
        
        if random.random() < epsilon:
            action = random.randint(0, OUTPUT_SIZE - 1)
        else:
            t_state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
            with torch.no_grad():
                action = policy_net(t_state).argmax().item()

        next_state, reward, done = env.step(action)
        
        memory.append((state, action, reward, next_state, done))
        state = next_state
        total_reward += reward

        if len(memory) >= BATCH_SIZE:
            batch = random.sample(memory, BATCH_SIZE)
            
            b_states = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=device)
            b_actions = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device).unsqueeze(1)
            b_rewards = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=device).unsqueeze(1)
            b_next_states = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=device)
            b_dones = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=device).unsqueeze(1)

            q_values = policy_net(b_states).gather(1, b_actions)
            
            with torch.no_grad():
                max_next_q_values = target_net(b_next_states).max(1)[0].unsqueeze(1)
                target_q_values = b_rewards + GAMMA * max_next_q_values * (1 - b_dones)

            loss = nn.MSELoss()(q_values, target_q_values)

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(policy_net.parameters(), max_norm=1.0)
            optimizer.step()

    epsilon = max(epsilon_min, epsilon * epsilon_decay)

    save_data(episode, env.score, steps)

    if episode % TARGET_UPDATE == 0:
        target_net.load_state_dict(policy_net.state_dict())

    if episode % 10 == 0:
        print(f"Ep {episode} | Score {env.score} | Reward {total_reward:.1f} | Epsilon {epsilon:.3f}")

    if episode % 100 == 0:
        torch.save(policy_net.state_dict(), SAVE_PATH)
        print("Model Salvo")