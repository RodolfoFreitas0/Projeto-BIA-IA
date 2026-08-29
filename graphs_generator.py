import os
import csv
import matplotlib.pyplot as plt

HUMAN_DIR = "Dados Humanos"
IA_DIR = "Dados IA"
CHARTS_DIR = "Graficos"

os.makedirs(CHARTS_DIR, exist_ok=True)

GAMES_CONFIG = {
    "1": {"name": "Sapo (Frogger)", "folder": "jogo_sapo", "csv_h": "dados_humano_sapo.csv", "csv_dqn": "dados_ia_sapo.csv", "csv_a2c": "dados_ia_sapo_a2c.csv"},
    "2": {"name": "Passaro (Flappy)", "folder": "jogo_passaro", "csv_h": "dados_humano_passaro.csv", "csv_dqn": "dados_ia_passaro.csv", "csv_a2c": "dados_ia_passaro_a2c.csv"},
    "3": {"name": "Desviar (Dodger)", "folder": "jogo_desviar", "csv_h": "dados_humano_desviar.csv", "csv_dqn": "dados_ia_desviar.csv", "csv_a2c": "dados_ia_desviar_a2c.csv"},
    "4": {"name": "Cobrinha (Snake)", "folder": "jogo_cobrinha", "csv_h": "dados_humano_cobrinha.csv", "csv_dqn": "dados_ia_cobrinha.csv", "csv_a2c": "dados_ia_cobrinha_a2c.csv"},
    "5": {"name": "Pulo (Jump)", "folder": "jogo_pulo", "csv_h": "dados_humano_pulo.csv", "csv_dqn": "dados_ia_pulo.csv", "csv_a2c": "dados_ia_pulo_a2c.csv"},
    "6": {"name": "Mira (Aim)", "folder": "jogo_mira", "csv_h": "dados_humano_mira.csv", "csv_dqn": "dados_ia_mira.csv", "csv_a2c": "dados_ia_mira_a2c.csv"},
    "7": {"name": "Ping (Pong)", "folder": "jogo_pong", "csv_h": "dados_humano_pong.csv", "csv_dqn": "dados_ia_pong_dqn.csv", "csv_a2c": "dados_ia_pong_a2c.csv"},
    "8": {"name": "Arkanoid", "folder": "jogo_arkanoid", "csv_h": "dados_humano_arkanoid.csv", "csv_dqn": "dados_ia_arkanoid_dqn.csv", "csv_a2c": "dados_ia_arkanoid_a2c.csv"},
    "9": {"name": "Pousar (Lunar Lander)", "folder": "jogo_pousar", "csv_h": "dados_humano_pousar.csv", "csv_dqn": "dados_ia_pousar_dqn.csv", "csv_a2c": "dados_ia_pousar_a2c.csv"}
}

def load_data(file_path):
    episodes = []
    scores = []
    
    if not os.path.exists(file_path):
        return episodes, scores
        
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader, None)
        if not header:
            return episodes, scores

        # Prefere a coluna "Reward" quando ela existir no CSV (ex: sapo DQN,
        # que agora salva o reward do episódio além do score 0/1). Se não
        # existir, cai de volta pra "Score", que é o que os outros jogos têm.
        header_lower = [h.strip().lower() for h in header]
        if "reward" in header_lower:
            value_idx = header_lower.index("reward")
        elif "score" in header_lower:
            value_idx = header_lower.index("score")
        else:
            value_idx = 1  # fallback pro formato antigo (Episodio, <valor>, ...)

        for row in reader:
            if row and len(row) > value_idx:
                try:
                    episodes.append(float(row[0]))
                    scores.append(float(row[value_idx]))
                except ValueError:
                    continue
                    
    return episodes, scores

def get_moving_average(data, window=50):
    if len(data) < window:
        return data
    
    moving_avg = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        slice_data = data[start:i+1]
        moving_avg.append(sum(slice_data) / len(slice_data))
    return moving_avg

def generate_chart(config):
    game_name = config["name"]
    
    path_h = os.path.join(HUMAN_DIR, config["csv_h"])
    path_dqn = os.path.join(IA_DIR, config["csv_dqn"])
    path_a2c = os.path.join(IA_DIR, config["csv_a2c"])
    
    ep_h, score_h = load_data(path_h)
    ep_dqn, score_dqn = load_data(path_dqn)
    ep_a2c, score_a2c = load_data(path_a2c)

    if not ep_dqn and not ep_a2c and not ep_h:
        print(f"\n[ERRO] Nenhum dado encontrado para {game_name}.")
        return

    plt.figure(figsize=(12, 6))

    # Apenas as medias moveis sao plotadas (curvas "Raw" removidas)
    if ep_dqn:
        score_dqn_smooth = get_moving_average(score_dqn, window=100)
        plt.plot(ep_dqn, score_dqn_smooth, color='blue', linewidth=2, label='DQN (Media Movel)')

    if ep_a2c:
        score_a2c_smooth = get_moving_average(score_a2c, window=100)
        plt.plot(ep_a2c, score_a2c_smooth, color='green', linewidth=2, label='A2C (Media Movel)')

    if not os.path.exists(path_h):
        print(f"Baseline humano ausente: {path_h}")

    if ep_h:
        human_mean = sum(score_h) / len(score_h)
        plt.axhline(y=human_mean, color='red', linestyle='--', linewidth=2.5, 
                    label=f'Baseline Humano (Media: {human_mean:.1f})')

    plt.title(f'Desempenho: Humano vs IA (DQN e A2C) - {game_name}', fontsize=16, fontweight='bold')
    plt.xlabel('Episodios', fontsize=12)
    plt.ylabel('Score / Reward', fontsize=12)
    plt.legend(loc='upper left', fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    
    file_name = os.path.join(CHARTS_DIR, f'resultado_{config["folder"]}.png')
    plt.savefig(file_name, dpi=300, bbox_inches='tight')
    print(f"\nSalvo como: {file_name}")
    
    plt.show()

def main():
    print("="*50)
    print("   GERADOR DE GRAFICOS")
    print("="*50)
    
    for key, config in GAMES_CONFIG.items():
        print(f"[{key}] - {config['name']}")
    print("[0] - Sair")
    
    while True:
        choice = input("\nEscolha o numero do jogo: ")
        
        if choice == "0":
            break
        elif choice in GAMES_CONFIG:
            generate_chart(GAMES_CONFIG[choice])
        else:
            print("Invalido.")

if __name__ == "__main__":
    try:
        import matplotlib
    except ImportError:
        print("Instale o matplotlib: pip install matplotlib")
        exit()
        
    main()