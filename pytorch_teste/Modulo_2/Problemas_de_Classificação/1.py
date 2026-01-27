### Rede Neural de Classificação com PyTorch

## 1. Dados

# Vamos usar uma library chamada Scikit-Learn para criar os dados

import sklearn
import torch
import torch.nn as nn
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split

# 1000 amostras de dados
n_samples = 1000

# Criar circulos
X, y = make_circles(
    n_samples, # Quantidade de circulos
    noise=0.03, # Pequena aleatoriedade
    random_state=42 # Seed manual
    )

# Checando
print(len(X), len(y))
print()

print(f"5 Primeiras amostras de X:\n {X[:5]} \n")
print(f"5 Primeiras amostras de y:\n {y[:5]} \n")

circles = pd.DataFrame({"X1": X[:, 0],
                        "X2": X[:, 1],
                        "label": y})

print(circles.head(10))
print()

plt.scatter(
    x=X[:, 0],
    y=X[:, 1],
    c=y,
    cmap=plt.cm.RdYlBu
    )

# plt.show()

# Obs: Os dados trabalhados nesse estudo são chamados de "toy dataset", um conjunto de dados que é pequeno o suficiente para ser experimentado e grande o suficiente
#      para usa-lo para praticar.

## Transformando os dados em Tensors, criando train split e test split

print(type(X), type(y))
print()

X = torch.from_numpy(X).type(torch.float32)
y = torch.from_numpy(y).type(torch.float32)

print(X[:5])
print()
print(y[:5])
print()

print(type(X), X.dtype, y.dtype)
print()

# Separando os dados

X_train, X_test, y_train, y_test = train_test_split(X,
                                                    y,
                                                    test_size=0.2, # 0.2 = 20% = Test, 80% = Train
                                                    random_state=42 # Seed manual
                                                    )

print(len(X_train), len(X_test), len(y_train), len(y_test))
print()

## Criando o modelo

# O modelo vai classificar os pontos vermelhos e azuis.

# 1. Criar a parte do codigo que coloca o processamento no aparelho disponivel.
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
print()

# 2. Construir o modelo que é subclasse de nn.module

class CircleModelV0(nn.Module):
    def __init__(self):
        super().__init__()
        # Criar 2 layers nn.Linear capazes de lidar com os dados
        self.layer_1 = nn.Linear(in_features=2, # Isso é igual 2 pois caso você cheque o X_train.shape, perceberemos que o formato do tensor ([X, 2]) -> 2 inputs.
                                 out_features=4
                                 ) # -> recebe 2 inputs e aumenta para 4 outputs
        
        self.layer_2 = nn.Linear(in_features=4, # O input do layer_2 deve ser igual ao output do layer_1
                                 out_features=1 # Esse valor é igual a 1 pois o y_train.shape é 1.
                                 ) # -> recebe 4 inputs do layer_1 e diminui para 1 output

        # ou...
        self.two_linear_layers = nn.Sequential(
            nn.Linear(in_features=2, out_features=5),
            nn.Linear(in_features=5, out_features=1)     
        )

    def forward(self, x):
        return self.layer_2(self.layer_1(x)) # x -> layer_1 -> layer_2 -> output
        # return self.two_linear_layers(x)
    
model_0 = CircleModelV0().to(device)

print(model_0)
print()

print(next(model_0.parameters()).device)
print()

# Vamos testar mudar o modelo para nn.Sequential

model_0 = nn.Sequential(
    nn.Linear(in_features=2, out_features=5),
    nn.Linear(in_features=5, out_features=1)
).to(device)

print(model_0)
print()

print(model_0.state_dict())
print()

# Testes sem treino

with torch.inference_mode():
    untrained_preds = model_0(X_test.to(device))

print(f"Quantidade de previsões: {len(untrained_preds)}, Shape: {untrained_preds.shape}")
print(f"Quantidade de dados de teste: {len(X_test)}, Shape: {X_test.shape}")

print(f"\nPrimeiras 10 previsões:\n{untrained_preds[:10]}")
print(f"\nPrimeiros 10 'rotulos':\n{y_test[:10]}")
print()

# Vamos escolher uma Loss Function e um Optimizer

# Nos modelos anteriores (RegressionModule) nós poderiamos usar coisas como MAE e MSE(Mean Absolute Error e Mean Squared Error)

# Num modelo de classificação como esse nos devemos usar coisas como Binary Cross Entropy ou Categorical Cross Entropy (ou Cross Entropy apenas)

# Para Optimizers, os dois mais comuns são SGD e Adam, apesar disso, o PyTorch possui varias outras opções prontas.

# -> Para a Loss Function (neste caso) vamos usar a "torch.nn.BECWithLogitsLoss()".
loss_fn = nn.BCEWithLogitsLoss()

optimizer = torch.optim.SGD(
    params=model_0.parameters(),
    lr=0.1
    )

## Calculo de precissão
def accucarry_fn(y_true, y_pred):
    correct = torch.eq(y_true, y_pred).sum().item()
    acc = (correct/len(y_pred)) * 100
    return acc

# Obs: O output "cru" do modelo é chamado logit
# Nos podemos converter esses logits em "probabilidades de previsão" passando eles por algum tipo de função de ativação
# (Função de ativação: sigmoid para classificação binaria e softmax para classificação de multiclasse)

model_0.eval()
with torch.inference_mode():
    y_logits = model_0(X_test.to(device))[:5]

print(y_logits)
print()

# Vamos usar a "sigmoid activation function" nos logits do modelo para transformalos em previsões
y_pred_probs = torch.sigmoid(y_logits)
print(y_pred_probs)
print()

print(torch.round(y_pred_probs))
print()

# Para os valores de probabilidade da nossa previsão, precisamos realizar um arredondamento no estilo de intervalo neles.

# y_pred_probs >= 0.5, y=1 (class 1)
# y_pred_probs < 0.5, y=0 (class 0)

y_preds = torch.round(y_pred_probs)

# logits -> pred probs -> pred labels
y_pred_labels = torch.round(torch.sigmoid(model_0(X_test.to(device))[:5]))

# Checar se são iguais
print(torch.eq(y_preds.squeeze(), y_pred_labels.squeeze()))

# Remove a dimensão extra
y_preds.squeeze()
print(y_preds)
print()

print(y_test[:5])
print()

## Vamos treinar o modelo

# Foward pass
# Calculate the loss
# Optimizer zero grad
# Loss backward
# Optimizer step

torch.manual_seed(42)
torch.cuda.manual_seed(42)

epochs = 1000

X_train, y_train = X_train.to(device), y_train.to(device)
X_test, y_test = X_test.to(device), y_test.to(device)

for epoch in range(epochs):
    model_0.train()

    y_logits = model_0(X_train).squeeze()
    y_pred = torch.round(torch.sigmoid(y_logits))

    loss = loss_fn(y_logits)