import os
import torch
import random
import csv
import numpy as np
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
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_pulo_dqn.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Score", "Passos"])

INPUT_SIZE = 7
OUTPUT_SIZE = 2

model = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_model = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_model.load_state_dict(model.state_dict())
target_model.eval()

optimizer = optim.Adam(model.parameters(), lr=0.001)

if os.path.exists(SAVE_PATH):
    checkpoint = torch.load(SAVE_PATH, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        model.load_state_dict(checkpoint["model_state_dict"])
        if "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
    else:
        model.load_state_dict(checkpoint)
    target_model.load_state_dict(model.state_dict())
    print("Modelo carregado!")

gamma = 0.99
epsilon = 1.0
epsilon_decay = 0.999985
epsilon_min = 0.01
BATCH_SIZE = 64
WARMUP_STEPS = 2000
GRAD_CLIP_NORM = 10.0
N_STEP = 5
PER_ALPHA = 0.6
PER_BETA_START = 0.4
PER_BETA_FRAMES = 200000
PER_EPS = 1e-6

class SumTree:
    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = np.zeros(2 * capacity - 1)
        self.data = [None] * capacity
        self.write = 0
        self.size = 0

    def _propagate(self, idx, change):
        parent = (idx - 1) // 2
        self.tree[parent] += change
        if parent != 0:
            self._propagate(parent, change)

    def _retrieve(self, idx, s):
        left = 2 * idx + 1
        right = left + 1
        if left >= len(self.tree):
            return idx
        if s <= self.tree[left]:
            return self._retrieve(left, s)
        return self._retrieve(right, s - self.tree[left])

    def total(self):
        return self.tree[0]

    def add(self, priority, data):
        idx = self.write + self.capacity - 1
        self.data[self.write] = data
        self.update(idx, priority)
        self.write = (self.write + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def update(self, idx, priority):
        change = priority - self.tree[idx]
        self.tree[idx] = priority
        self._propagate(idx, change)

    def get(self, s):
        idx = self._retrieve(0, s)
        data_idx = idx - self.capacity + 1
        return idx, self.tree[idx], self.data[data_idx]

class PrioritizedReplayBuffer:
    def __init__(self, capacity, alpha=PER_ALPHA):
        self.tree = SumTree(capacity)
        self.alpha = alpha
        self.max_priority = 1.0

    def push(self, transition):
        priority = self.max_priority ** self.alpha
        self.tree.add(priority, transition)

    def sample(self, batch_size, beta):
        batch, idxs, priorities = [], [], []
        segment = self.tree.total() / batch_size

        for i in range(batch_size):
            a = segment * i
            b = segment * (i + 1)
            s = random.uniform(a, b)
            idx, priority, data = self.tree.get(s)
            batch.append(data)
            idxs.append(idx)
            priorities.append(priority)

        sampling_probs = np.array(priorities) / self.tree.total()
        weights = (self.tree.size * sampling_probs) ** (-beta)
        weights /= weights.max()

        return batch, idxs, weights

    def update_priorities(self, idxs, td_errors):
        for idx, td_error in zip(idxs, td_errors):
            priority = (abs(td_error) + PER_EPS) ** self.alpha
            self.tree.update(idx, priority)
            self.max_priority = max(self.max_priority, priority)

    def __len__(self):
        return self.tree.size

memory = PrioritizedReplayBuffer(capacity=50000)

def compute_nstep_transition(n_step_buffer):
    R = 0.0
    for i, (_, _, r, _, d) in enumerate(n_step_buffer):
        R += (gamma ** i) * r
        if d:
            break

    state0, action0, _, _, _ = n_step_buffer[0]
    _, _, _, next_state_n, done_n = n_step_buffer[-1]
    gamma_pow = gamma ** len(n_step_buffer)

    return state0, action0, R, next_state_n, done_n, gamma_pow

def beta_by_frame(frame_idx):
    return min(1.0, PER_BETA_START + frame_idx * (1.0 - PER_BETA_START) / PER_BETA_FRAMES)

def choose_action(state):
    if random.random() < epsilon:
        return random.randint(0, 1)
    
    with torch.no_grad():
        s = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        q_values = model(s)
        return torch.argmax(q_values).item()

def train_batch(frame_idx):
    if len(memory) < max(BATCH_SIZE, WARMUP_STEPS):
        return

    beta = beta_by_frame(frame_idx)
    batch, idxs, weights = memory.sample(BATCH_SIZE, beta)

    states = torch.tensor([b[0] for b in batch], dtype=torch.float32, device=device)
    actions = torch.tensor([b[1] for b in batch], dtype=torch.long, device=device)
    returns_n = torch.tensor([b[2] for b in batch], dtype=torch.float32, device=device)
    next_states = torch.tensor([b[3] for b in batch], dtype=torch.float32, device=device)
    dones = torch.tensor([b[4] for b in batch], dtype=torch.float32, device=device)
    gamma_pows = torch.tensor([b[5] for b in batch], dtype=torch.float32, device=device)
    weights_t = torch.tensor(weights, dtype=torch.float32, device=device)

    q_values = model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

    with torch.no_grad():
        next_actions = model(next_states).argmax(1)
        next_q = target_model(next_states).gather(1, next_actions.unsqueeze(1)).squeeze(1)
        target = returns_n + gamma_pows * next_q * (1 - dones)

    td_errors = (q_values - target).detach().cpu().numpy()

    per_sample_loss = nn.SmoothL1Loss(reduction='none')(q_values, target)
    loss = (per_sample_loss * weights_t).mean()

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=GRAD_CLIP_NORM)
    optimizer.step()

    memory.update_priorities(idxs, td_errors)

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
    n_step_buffer = deque(maxlen=N_STEP)

    while True:
        total_steps += 1
        steps += 1
        
        action = choose_action(state)
        next_state, reward, done = env.step(action)

        n_step_buffer.append((state, action, reward, next_state, done))
        if len(n_step_buffer) == N_STEP:
            memory.push(compute_nstep_transition(n_step_buffer))

        state = next_state
        total_reward += reward

        epsilon = max(epsilon_min, epsilon * epsilon_decay)

        if total_steps % 4 == 0:
            train_batch(total_steps)

        if total_steps % 1000 == 0:
            target_model.load_state_dict(model.state_dict())

        if done:
            if len(n_step_buffer) == N_STEP:
                n_step_buffer.popleft()
            while len(n_step_buffer) > 0:
                memory.push(compute_nstep_transition(n_step_buffer))
                n_step_buffer.popleft()
            break
    
    scores.append(total_reward)
    
    save_data(episode, total_reward, steps)

    if episode % 100 == 0:
        torch.save({
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        }, SAVE_PATH)
        print("Modelo Salvo!")

    if episode % 10 == 0:
        print(f"Ep {episode} | Score {total_reward:.1f} | Epsilon {epsilon:.3f}")