# Como treinar seu próprio modelo

Este texto explica o passo a passo genérico que vale para QUALQUER jogo da
pasta `Jogos&Algoritmos/`. As instruções específicas de cada jogo (controles,
tempo estimado de treino, etc.) estão nos arquivos individuais
(`INSTRUCOES_<jogo>.md`).

## 1. Pré-requisitos

- Python 3.10+ instalado
- As bibliotecas usadas no projeto:

```bash
pip install torch pygame numpy
```

(Se quiser isolar as dependências do resto do seu sistema, crie um ambiente
virtual antes: `python -m venv .venv` e ative com `.venv\Scripts\activate`
no Windows ou `source .venv/bin/activate` no Linux/Mac.)

## 2. Estrutura que você vai usar

Cada jogo tem uma pasta pra cada algoritmo, por exemplo:

```
Jogos&Algoritmos/
  jogo_pong/
    pong_env_A2C/
      pong_env.py      <- o "jogo" em si (regras, física, recompensas)
      pong_model.py     <- a rede neural
      pong_train.py      <- ESSE você roda pra treinar
      pong_watch.py       <- ESSE você roda pra assistir a IA já treinada jogando
      pong_human.py        <- ESSE você roda pra jogar você mesmo
    pong_env_DQN/
      ... (mesma ideia, outro algoritmo)
```

Os modelos treinados são salvos automaticamente em `Models/<nome_do_jogo>/`,
e os dados de cada episódio de treino em `Dados IA/`.

## 3. Rodando um treino

1. Abra o terminal na pasta do algoritmo que quer treinar, por exemplo:
   ```bash
   cd "Jogos&Algoritmos/jogo_pong/pong_env_A2C"
   ```
2. Rode o script de treino:
   ```bash
   python pong_train.py
   ```
3. O terminal vai mostrar o progresso episódio a episódio (recompensa,
   pontuação, etc.). Isso pode demorar de minutos a várias horas dependendo
   do jogo e do algoritmo — veja o tempo estimado no arquivo de instrução de
   cada jogo.

O modelo é salvo **periodicamente durante o treino** (não só no final), então
é seguro interromper com `Ctrl+C` a qualquer momento sem perder o progresso.

## 4. Continuando um treino já começado

Não precisa fazer nada especial: se você rodar o `_train.py` de novo, ele
**carrega automaticamente** o modelo salvo em `Models/<jogo>/` (se existir) e
continua o treino a partir dali, em vez de começar do zero.

Se quiser treinar do zero de propósito, apague o arquivo `.pth` correspondente
em `Models/<jogo>/` antes de rodar.

## 5. Assistindo o modelo treinado jogar

Depois (ou durante) o treino, rode:

```bash
python pong_watch.py
```

Isso abre uma janela mostrando a IA jogando com o modelo mais recente salvo.

## 6. Jogando você mesmo (opcional)

```bash
python pong_human.py
```

Os controles variam por jogo — estão listados no arquivo de instrução de cada
um. Isso serve pra você comparar sua pontuação com a da IA, e os dados da sua
partida ficam salvos em `Dados Humanos/`.

## Resumo rápido

| Quero...                          | Rodo...          |
|-----------------------------------|------------------|
| Treinar (ou continuar treinando)  | `..._train.py`   |
| Ver a IA jogando                  | `..._watch.py`   |
| Jogar eu mesmo                    | `..._human.py`   |
