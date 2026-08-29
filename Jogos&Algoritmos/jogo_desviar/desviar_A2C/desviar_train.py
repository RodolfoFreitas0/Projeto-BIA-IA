import os
import csv
import torch
import torch.optim as optim
from torch.distributions import Categorical
from desviar_env import DodgerEnv
from desviar_model import A2C

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BASE_DIR = "Models"
GAME_NAME = "jogo_desviar"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)
SAVE_PATH = os.path.join(SAVE_DIR, "desviar_model_a2c.pth")

DATA_DIR = "Dados IA"
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_desviar_a2c.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Score", "Passos"])

INPUT_SIZE = 29
OUTPUT_SIZE = 5
GAMMA = 0.99
LR = 0.0001
MAX_EPISODES = 10000
BATCH_EPISODES = 5

model = A2C(INPUT_SIZE, OUTPUT_SIZE).to(device)

if os.path.exists(SAVE_PATH):
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    print("Modelo carregado!")

optimizer = optim.Adam(model.parameters(), lr=LR)
env = DodgerEnv(render=False)

def compute_loss(log_probs, values, rewards, entropies):
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + GAMMA * G
        returns.insert(0, G)

    returns = torch.tensor(returns, dtype=torch.float32, device=device)
    values = torch.cat(values).squeeze()
    log_probs = torch.cat(log_probs)
    entropies = torch.cat(entropies)

    critic_loss = torch.nn.functional.smooth_l1_loss(values, returns)

    unnormalized_advantage = (returns - values).detach()
    if unnormalized_advantage.numel() > 1:
        advantage = (unnormalized_advantage - unnormalized_advantage.mean()) / (unnormalized_advantage.std() + 1e-8)
    else:
        advantage = unnormalized_advantage

    actor_loss = -(log_probs * advantage).mean() - 0.1 * entropies.mean()

    total_loss = actor_loss + 0.5 * critic_loss

    total_loss.backward()

    return total_loss.item()

def save_data(episode, score, steps):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([episode, score, steps])

optimizer.zero_grad()

for episode in range(MAX_EPISODES):
    state = env.reset()

    logs, vals, rews, ents = [], [], [], []
    total_reward = 0
    steps = 0
    done = False

    while not done:
        steps += 1
        
        t_state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
        logits, val = model(t_state)

        dist = Categorical(logits=logits)
        action = dist.sample()

        next_state, reward, done = env.step(action.item())

        logs.append(dist.log_prob(action))
        vals.append(val)
        rews.append(reward)
        ents.append(dist.entropy())

        state = next_state
        total_reward += reward

    compute_loss(logs, vals, rews, ents)
    save_data(episode, env.score, steps)

    if (episode + 1) % BATCH_EPISODES == 0:
        torch.nn.utils.clip_grad_norm_(model.actor.parameters(), max_norm=0.5)
        torch.nn.utils.clip_grad_norm_(model.critic.parameters(), max_norm=0.5)
        torch.nn.utils.clip_grad_norm_(model.base.parameters(), max_norm=1.0)
        optimizer.step()
        optimizer.zero_grad()

    if episode % 10 == 0:
        print(f"Ep {episode} | Score {env.score} | Reward {total_reward:.1f}")

    if episode % 100 == 0:
        torch.save(model.state_dict(), SAVE_PATH)
        print("Model Salvo")