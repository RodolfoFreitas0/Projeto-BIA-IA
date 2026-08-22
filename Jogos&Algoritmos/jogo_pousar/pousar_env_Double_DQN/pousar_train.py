import os
import random
import csv
from collections import deque

import torch
import torch.nn as nn
import torch.optim as optim

from pousar_env import LunarLanderEnv
from pousar_model import DQN


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_pousar"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)

SAVE_PATH = os.path.join(SAVE_DIR, "pousar_model_DQN.pth")

DATA_DIR = "Dados IA"
os.makedirs(DATA_DIR, exist_ok=True)
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_pousar_dqn.csv")

INPUT_SIZE = 10
OUTPUT_SIZE = 4
BATCH_SIZE = 64
GAMMA = 0.99
LR = 0.00025
MAX_EPISODES = 50000
MEMORY_SIZE = 50000
TRAIN_EVERY = 4
LEARNING_STARTS = 2000
TARGET_UPDATE_EVERY = 10

EPSILON_START = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.9998

policy_net = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
target_net = DQN(INPUT_SIZE, OUTPUT_SIZE).to(device)
optimizer = optim.Adam(policy_net.parameters(), lr=LR)
loss_fn = nn.SmoothL1Loss()

epsilon = EPSILON_START
start_episode = 0
if os.path.exists(SAVE_PATH):
    checkpoint = torch.load(SAVE_PATH, map_location=device)
    if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
        policy_net.load_state_dict(checkpoint["model_state_dict"])
        target_net.load_state_dict(checkpoint.get("target_state_dict", checkpoint["model_state_dict"]))
        if "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        epsilon = checkpoint.get("epsilon", EPSILON_START)
        start_episode = checkpoint.get("episode", -1) + 1
    else:
        policy_net.load_state_dict(checkpoint)
        target_net.load_state_dict(policy_net.state_dict())
else:
    target_net.load_state_dict(policy_net.state_dict())

target_net.eval()
memory = deque(maxlen=MEMORY_SIZE)
env = LunarLanderEnv(render=False)

CSV_FIELDS = [
    "Episodio", "Score", "Passos", "Resultado", "Pousou", "Colisao",
    "Timeout", "VelocidadeAngularMedia", "VelocidadeAngularMaxima",
    "Epsilon", "LossMedia"
]
if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode="w", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=CSV_FIELDS).writeheader()


def train_step():
    if len(memory) < max(BATCH_SIZE, LEARNING_STARTS):
        return None

    batch = random.sample(memory, BATCH_SIZE)
    states = torch.tensor([item[0] for item in batch], dtype=torch.float32, device=device)
    actions = torch.tensor([item[1] for item in batch], dtype=torch.long, device=device).unsqueeze(1)
    rewards = torch.tensor([item[2] for item in batch], dtype=torch.float32, device=device)
    next_states = torch.tensor([item[3] for item in batch], dtype=torch.float32, device=device)
    dones = torch.tensor([item[4] for item in batch], dtype=torch.float32, device=device)

    q_values = policy_net(states).gather(1, actions).squeeze(1)

    with torch.no_grad():
        next_actions = policy_net(next_states).argmax(dim=1, keepdim=True)
        next_q_values = target_net(next_states).gather(1, next_actions).squeeze(1)
        target_q_values = rewards + GAMMA * next_q_values * (1.0 - dones)

    loss = loss_fn(q_values, target_q_values)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(policy_net.parameters(), max_norm=1.0)
    optimizer.step()
    return float(loss.item())


def save_data(row):
    with open(DATA_ARCHIVE, mode="a", newline="", encoding="utf-8") as file:
        csv.DictWriter(file, fieldnames=CSV_FIELDS).writerow(row)


def save_checkpoint(episode):
    torch.save({
        "episode": episode,
        "epsilon": epsilon,
        "model_state_dict": policy_net.state_dict(),
        "target_state_dict": target_net.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
    }, SAVE_PATH)


def mean(values):
    return sum(values) / len(values) if values else 0.0


recent_scores = deque(maxlen=100)
recent_landed = deque(maxlen=100)
recent_crashes = deque(maxlen=100)
recent_timeouts = deque(maxlen=100)
recent_angular = deque(maxlen=100)
global_step = 0

for episode in range(start_episode, MAX_EPISODES):
    state = env.reset()
    total_reward = 0.0
    steps = 0
    angular_sum = 0.0
    angular_max = 0.0
    episode_losses = []
    done = False

    while not done:
        global_step += 1
        steps += 1

        if random.random() < epsilon:
            action = random.randrange(OUTPUT_SIZE)
        else:
            with torch.no_grad():
                state_tensor = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
                action = policy_net(state_tensor).argmax(dim=1).item()

        next_state, reward, done = env.step(action)
        memory.append((state, action, reward, next_state, done))
        state = next_state
        total_reward += reward

        angular_speed = abs(env.ship.angular_vel)
        angular_sum += angular_speed
        angular_max = max(angular_max, angular_speed)

        if global_step >= LEARNING_STARTS and global_step % TRAIN_EVERY == 0:
            loss = train_step()
            if loss is not None:
                episode_losses.append(loss)

    outcome = getattr(env, "outcome", "crash" if done else "running")
    landed = int(outcome == "landed")
    crashed = int(outcome == "crash")
    timeout = int(outcome == "timeout")
    angular_mean = angular_sum / max(steps, 1)

    recent_scores.append(total_reward)
    recent_landed.append(landed)
    recent_crashes.append(crashed)
    recent_timeouts.append(timeout)
    recent_angular.append(angular_mean)

    save_data({
        "Episodio": episode,
        "Score": round(total_reward, 4),
        "Passos": steps,
        "Resultado": outcome,
        "Pousou": landed,
        "Colisao": crashed,
        "Timeout": timeout,
        "VelocidadeAngularMedia": round(angular_mean, 6),
        "VelocidadeAngularMaxima": round(angular_max, 6),
        "Epsilon": round(epsilon, 6),
        "LossMedia": round(mean(episode_losses), 6),
    })

    epsilon = max(EPSILON_MIN, epsilon * EPSILON_DECAY)

    if episode % TARGET_UPDATE_EVERY == 0:
        target_net.load_state_dict(policy_net.state_dict())

    if episode % 10 == 0:
        print(
            f"Ep {episode:6d} | Score {total_reward:8.2f} | Resultado {outcome:7s} | "
            f"Pousos100 {100 * mean(recent_landed):5.1f}% | "
            f"Colisoes100 {100 * mean(recent_crashes):5.1f}% | "
            f"Timeouts100 {100 * mean(recent_timeouts):5.1f}% | "
            f"AngVel100 {mean(recent_angular):.3f} | Eps {epsilon:.3f}"
        )

    if episode % 100 == 0:
        save_checkpoint(episode)
        print(f"Checkpoint salvo em {SAVE_PATH}")

save_checkpoint(MAX_EPISODES - 1)
print("Treino concluido.")
