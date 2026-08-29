import os
import torch
import random
import csv
import torch.nn as nn
import torch.optim as optim
from collections import deque
from pong_model import DQN
from pong_env import PongEnv

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo: ", device)

env = PongEnv(render=False, player=False)

BASE_DIR = "Models"
GAME_NAME = "jogo_pong"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)

DATA_DIR = "Dados IA"
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_pong_dqn.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Reward Direita", "Reward Esquerda", "Passos"])

INPUT_SIZE = 7
OUTPUT_SIZE = 3

model_R = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_model_R = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_model_R.load_state_dict(model_R.state_dict())
target_model_R.eval()
optimizer_R = optim.Adam(model_R.parameters(), lr=0.0001)
memory_R = deque(maxlen=50000)

model_L = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_model_L = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_model_L.load_state_dict(model_L.state_dict())
target_model_L.eval()
optimizer_L = optim.Adam(model_L.parameters(), lr=0.0001)
memory_L = deque(maxlen=50000)

SAVE_PATH_R = os.path.join(SAVE_DIR, "pong_model_dqn_R.pth")
SAVE_PATH_L = os.path.join(SAVE_DIR, "pong_model_dqn_L.pth")

if os.path.exists(SAVE_PATH_R) and os.path.exists(SAVE_PATH_L):
    model_R.load_state_dict(torch.load(SAVE_PATH_R, map_location=device))
    model_L.load_state_dict(torch.load(SAVE_PATH_L, map_location=device))
    print("Modelos carregados!")

gamma = 0.99
epsilon = 1.0
epsilon_decay = 0.997
epsilon_min = 0.01
BATCH_SIZE = 64

def choose_action(state, model_net):
    if random.random() < epsilon:
        return random.randint(0, 2)
    
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        q_values = model_net(s)
        return torch.argmax(q_values).item()

def train_batch(model_net, target_net, opt, mem):
    if len(mem) < 1000:
        return
    
    batch = random.sample(mem, BATCH_SIZE)

    states = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=device)
    actions = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device)
    rewards = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=device)
    next_states = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=device)
    dones = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=device)

    q_values = model_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)

    with torch.no_grad():
        next_q = target_net(next_states).max(1)[0]
        target = rewards + gamma * next_q * (1 - dones)
    
    loss = nn.HuberLoss()(q_values, target)

    opt.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model_net.parameters(), max_norm=1.0)
    opt.step()

def save_data(episode, rwd_R, rwd_L, steps):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([episode, rwd_R, rwd_L, steps])

total_steps = 0

for episode in range(10001):
    state = env.reset()
    tot_R, tot_L = 0, 0
    steps = 0

    while True:
        total_steps += 1
        steps += 1
        
        state_R, state_L = state
        
        act_R = choose_action(state_R, model_R)
        act_L = choose_action(state_L, model_L)
        
        next_state_R, next_state_L, rwd_R, rwd_L, done = env.step(act_R, act_L)

        memory_R.append((state_R, act_R, rwd_R, next_state_R, done))
        memory_L.append((state_L, act_L, rwd_L, next_state_L, done))
        
        state = (next_state_R, next_state_L)
        tot_R += rwd_R
        tot_L += rwd_L
    
        if total_steps % 4 == 0:
            train_batch(model_R, target_model_R, optimizer_R, memory_R)
            train_batch(model_L, target_model_L, optimizer_L, memory_L)

        if total_steps % 1000 == 0:
            target_model_R.load_state_dict(model_R.state_dict())
            target_model_L.load_state_dict(model_L.state_dict())

        if done:
            break
    
    epsilon = max(epsilon_min, epsilon * epsilon_decay)
    
    save_data(episode, tot_R, tot_L, steps)

    if episode % 100 == 0:
        torch.save(model_R.state_dict(), SAVE_PATH_R)
        torch.save(model_L.state_dict(), SAVE_PATH_L)
        print("Modelos salvos")

    if episode % 10 == 0:
        print(f"Ep {episode:5d} | Direita {tot_R:05.1f} | Esquerda {tot_L:05.1f} | Epsilon {epsilon:.3f}")