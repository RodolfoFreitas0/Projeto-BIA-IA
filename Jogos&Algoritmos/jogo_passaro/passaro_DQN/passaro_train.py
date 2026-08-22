import os
import random
import csv
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
from passaro_env import FlappyEnv
from passaro_model import DQN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo:", device)

BASE_DIR = "Models"
GAME_NAME = "jogo_passaro"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "passaro_model_DQN.pth")

DATA_DIR = "Dados IA"
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_passaro.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Score", "Passos"])

INPUT_SIZE = 5
OUTPUT_SIZE = 2
BATCH_SIZE = 64
GAMMA = 0.99
LR = 0.0005
MAX_EPISODES = 10000

epsilon = 1.0
epsilon_min = 0.01
epsilon_decay = 0.995

policy_net = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_net = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    policy_net.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")

target_net.load_state_dict(policy_net.state_dict())
target_net.eval()

optimizer = optim.Adam(policy_net.parameters(), lr=LR)
loss_fn = nn.MSELoss()

memory = deque(maxlen=50000)
env = FlappyEnv(render=False)

def train_step():
    if len(memory) < BATCH_SIZE:
        return
        
    batch = random.sample(memory, BATCH_SIZE)
    
    states = torch.tensor([x[0] for x in batch], dtype=torch.float32, device=device)
    actions = torch.tensor([x[1] for x in batch], dtype=torch.long, device=device).unsqueeze(1)
    rewards = torch.tensor([x[2] for x in batch], dtype=torch.float32, device=device)
    next_states = torch.tensor([x[3] for x in batch], dtype=torch.float32, device=device)
    dones = torch.tensor([x[4] for x in batch], dtype=torch.float32, device=device)

    q_values = policy_net(states).gather(1, actions).squeeze()
    
    with torch.no_grad():
        max_next_q_values = target_net(next_states).max(1)[0]
        target_q_values = rewards + (GAMMA * max_next_q_values * (1 - dones))

    loss = loss_fn(q_values, target_q_values)
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

def save_data(episode, score, steps):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([episode, score, steps])

global_step = 0

for episode in range(MAX_EPISODES):
    state = env.reset()
    total_reward = 0
    done = False
    steps = 0
    
    while not done:
        global_step += 1
        steps += 1
        
        if random.random() < epsilon:
            action = random.randint(0, OUTPUT_SIZE - 1)
        else:
            with torch.no_grad():
                s_tensor = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
                action = torch.argmax(policy_net(s_tensor)).item()
                
        next_state, reward, done = env.step(action)
        memory.append((state, action, reward, next_state, done))
        
        state = next_state
        total_reward += reward
        
        if global_step % 4 == 0:
            train_step()

    save_data(episode, env.score, steps)

    if epsilon > epsilon_min:
        epsilon *= epsilon_decay
        
    if episode % 10 == 0:
        target_net.load_state_dict(policy_net.state_dict())
        print(f"Ep {episode} | Score {env.score} | Reward {total_reward:.1f} | Epsilon {epsilon:.3f}")
        
    if episode % 100 == 0:
        torch.save(policy_net.state_dict(), SAVE_PATH)
        print("Modelo salvo!")