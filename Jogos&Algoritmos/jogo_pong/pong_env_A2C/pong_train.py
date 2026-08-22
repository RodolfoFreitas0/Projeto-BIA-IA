import os
import csv
import torch
import torch.optim as optim
from torch.distributions import Categorical
from pong_model import A2C
from pong_env import PongEnv

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Dispositivo: ", device)

BASE_DIR = "Models"
GAME_NAME = "jogo_pong"
SAVE_DIR = os.path.join(BASE_DIR, GAME_NAME)
os.makedirs(SAVE_DIR, exist_ok=True)

DATA_DIR = "Dados IA"
DATA_ARCHIVE = os.path.join(DATA_DIR, "dados_ia_pong.csv")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.isfile(DATA_ARCHIVE):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episodio", "Reward Direita", "Reward Esquerda", "Passos"])

model_R = A2C().to(device)
model_L = A2C().to(device)

SAVE_PATH_R = os.path.join(SAVE_DIR, "pong_model_a2c_R.pth")
SAVE_PATH_L = os.path.join(SAVE_DIR, "pong_model_a2c_L.pth")

if os.path.exists(SAVE_PATH_R) and os.path.exists(SAVE_PATH_L):
    model_R.load_state_dict(torch.load(SAVE_PATH_R, map_location=device))
    model_L.load_state_dict(torch.load(SAVE_PATH_L, map_location=device))
    print("Modelos Carregados")

optimizer_R = optim.Adam(model_R.parameters(), lr=0.0005)
optimizer_L = optim.Adam(model_L.parameters(), lr=0.0005)

env = PongEnv(render=False, player=False)
gamma = 0.99

def update_model(optimizer, log_probs, values, rewards, entropies):
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    
    returns = torch.tensor(returns, dtype=torch.float32, device=device)
    values = torch.cat(values).squeeze()
    log_probs = torch.cat(log_probs)
    entropies = torch.cat(entropies)

    advantage = returns - values

    critic_loss = advantage.pow(2).mean()

    advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-8)

    entropy_loss = entropies.mean()
    actor_loss = -(log_probs * advantage.detach()).mean() - 0.01 * entropy_loss

    total_loss = actor_loss + 0.5 * critic_loss

    optimizer.zero_grad()
    total_loss.backward()

    torch.nn.utils.clip_grad_norm_(model_R.parameters(), max_norm=0.5)
    torch.nn.utils.clip_grad_norm_(model_L.parameters(), max_norm=0.5)

    optimizer.step()

    return total_loss.item()

def save_data(episode, reward_R, reward_L, steps):
    with open(DATA_ARCHIVE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([episode, reward_R, reward_L, steps])

for episode in range(10001):
    state = env.reset()

    logs_R, vals_R, rews_R, ents_R = [], [], [], []
    logs_L, vals_L, rews_L, ents_L = [], [], [], []

    tot_R, tot_L = 0, 0
    steps = 0
    done = False

    while not done:
        steps += 1
        state_R, state_L = state

        t_R = torch.tensor(state_R, dtype=torch.float32, device=device).unsqueeze(0)
        logits_R, val_R = model_R(t_R)
        dist_R = Categorical(logits=logits_R)
        act_R = dist_R.sample()

        t_L = torch.tensor(state_L, dtype=torch.float32, device=device).unsqueeze(0)
        logits_L, val_L = model_L(t_L)
        dist_L = Categorical(logits=logits_L)
        act_L = dist_L.sample()

        next_state_R, next_state_L, rwd_R, rwd_L, done = env.step(act_R.item(), act_L.item())

        logs_R.append(dist_R.log_prob(act_R))
        vals_R.append(val_R)
        rews_R.append(rwd_R)
        ents_R.append(dist_R.entropy())

        logs_L.append(dist_L.log_prob(act_L))
        vals_L.append(val_L)
        rews_L.append(rwd_L)
        ents_L.append(dist_L.entropy())

        state = (next_state_R, next_state_L)
        tot_R += rwd_R
        tot_L += rwd_L
    
    update_model(optimizer_R, logs_R, vals_R, rews_R, ents_R)
    update_model(optimizer_L, logs_L, vals_L, rews_L, ents_L)
    
    save_data(episode, tot_R, tot_L, steps)

    if episode % 100 == 0:
        torch.save(model_R.state_dict(), SAVE_PATH_R)
        torch.save(model_L.state_dict(), SAVE_PATH_L)
        print("Modelos Salvos")

    if episode % 10 == 0:
        print(f"Ep {episode} | Direita {tot_R:05.1f} | Esquerda {tot_L:05.1f}")