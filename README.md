[README.md](https://github.com/user-attachments/files/31337623/README.md)
# Jogos e Algoritmos: Pygame, DQN e A2C

Projeto experimental de aprendizado por reforço aplicado a nove mini jogos desenvolvidos em Python. O projeto reúne versões jogáveis com Pygame e versões treinadas com redes neurais usando Deep Q-Network (DQN) e Advantage Actor-Critic (A2C).

A proposta é comparar como diferentes algoritmos aprendem a interagir com ambientes, observar estados, escolher ações e receber recompensas.

## Contexto acadêmico

Este projeto integra o plano de trabalho **Implementação e Análise de Agentes de Aprendizado por Reforço em Jogos Digitais**, desenvolvido no âmbito do Programa Institucional de Bolsa de Incentivo Acadêmico (BIA), com apoio da [FACEPE](https://www.facepe.br/) e da [UFRPE](https://www.ufrpe.br/), no curso de Bacharelado em Engenharia de Computação.

O projeto combina desenvolvimento de software, desenvolvimento de jogos e inteligência artificial para criar um ambiente didático e experimental acessível em computadores de uso comum. Além do caráter técnico, a proposta está relacionada às dimensões de ensino, pesquisa e extensão, por meio da documentação e da disponibilização dos resultados.

## Objetivo

O objetivo é desenvolver jogos digitais com agentes inteligentes baseados em aprendizado por reforço, permitindo analisar seu desempenho, sua estabilidade, sua eficiência e sua aplicabilidade em diferentes tipos de jogos.

Para isso, cada jogo é transformado em um ambiente com observações, ações, recompensas e condições de término. Os agentes são treinados e avaliados com métricas como pontuação, vitórias, tempo de treinamento, estabilidade e uso de recursos computacionais.

## Metodologia

O plano de trabalho organiza o desenvolvimento em ciclos incrementais. As principais etapas foram:

1. definir os requisitos, regras e mecânicas dos jogos;
2. implementar e testar versões funcionais dos jogos;
3. modelar os ambientes de aprendizado por reforço;
4. desenvolver e treinar os agentes DQN e A2C;
5. comparar os resultados com partidas humanas e métricas específicas;
6. documentar e divulgar o código, os resultados e as lições aprendidas.

## Jogos Desenvolvidos

Os nove jogos principais construídos e utilizados para o treinamento dos agentes são:

| Jogo | Objetivo |
|---|---|
| **Sapo / Frogger** | Atravessar o cenário sem colidir com obstáculos |
| **Pássaro / Flappy** | Passar entre obstáculos |
| **Desviar / Dodger** | Sobreviver evitando inimigos |
| **Cobrinha / Snake** | Comer a comida e evitar colisões |
| **Pulo / Jump** | Pular obstáculos e avançar |
| **Mira / Aim** | Mover o cursor e atingir alvos |
| **Pong** | Rebater a bola e marcar pontos |
| **Arkanoid** | Rebater a bola e destruir blocos |
| **Pousar / Lunar Lander** | Controlar uma nave até uma plataforma |

## Começando

Estas instruções permitirão que você obtenha uma cópia do projeto em funcionamento na sua máquina local para desenvolvimento, testes e execução dos jogos.

### Pré-requisitos

Para executar o projeto, é necessário ter Python 3 instalado. Também são necessárias as bibliotecas Pygame, PyTorch, Matplotlib e NumPy.

```bash
python --version
python -m pip --version
```

No Windows, caso o comando `python` não esteja disponível, tente utilizar `py`. No Linux ou macOS, pode ser necessário utilizar `python3` e `pip3`.

### Instalação

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/RodolfoFreitas0/Projeto-BIA-IA.git
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

No Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências principais:

```bash
python -m pip install --upgrade pip
python -m pip install pygame matplotlib numpy torch
```

Caso seja necessário utilizar GPU, instale a versão do PyTorch compatível com o sistema pelo [site oficial do PyTorch](https://pytorch.org/get-started/locally/).

## Executando os testes

A validação disponível é feita por compilação dos arquivos Python, execução dos jogos, execução dos ambientes e observação dos modelos treinados.

Para verificar se os arquivos Python podem ser interpretados sem erros de sintaxe, execute na raiz do projeto:

```bash
python -m compileall Jogos_Algoritmos
```

## Construído com

- [Python](https://www.python.org/) — Linguagem de programação utilizada no projeto.
- [Pygame](https://www.pygame.org/) — Biblioteca usada para criar os jogos, as interfaces, os eventos e as colisões.
- [PyTorch](https://pytorch.org/) — Framework usado para tensores, redes neurais e treinamento dos agentes.
- [Matplotlib](https://matplotlib.org/) — Biblioteca usada para gerar os gráficos de desempenho.
- [NumPy](https://numpy.org/) — Biblioteca de apoio para operações numéricas.
- [Git](https://git-scm.com/) e [GitHub](https://github.com/) — Ferramentas usadas para versionamento e publicação do projeto.

## Execução

Os comandos devem ser executados a partir da raiz do repositório.

Para executar qualquer script de um jogo, use o formato geral:

```bash
python Jogos_Algoritmos/<jogo>/<versao>/<script>.py
```

Exemplo com o jogo do Sapo:

```bash
python Jogos_Algoritmos/jogo_sapo/sapo_pygame/mainPygame.py
```

Para treinar uma DQN:

```bash
python Jogos_Algoritmos/<jogo>/<jogo>_DQN/<jogo>_train.py
```

Para treinar um A2C:

```bash
python Jogos_Algoritmos/<jogo>/<jogo>_A2C/<jogo>_train.py
```

Para visualizar um modelo treinado:

```bash
python Jogos_Algoritmos/<jogo>/<jogo>_DQN/<jogo>_watch.py
```

Para gerar os gráficos:

```bash
python graphs_generator.py
```
