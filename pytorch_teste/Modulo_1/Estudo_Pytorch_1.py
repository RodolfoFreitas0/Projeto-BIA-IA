import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

weight = 0.7
bias = 0.3

start = 0
end = 1
step = 0.02
X = torch.arange(start, end, step).unsqueeze(dim=1)
y = weight * X + bias

print(f"X = {X[:10]}\n")
print(f"y = {y[:10]}\n")

train_split = int(0.8 * len(X)) # <- (40 Samples)
X_train, y_train = X[:train_split], y[:train_split]
X_test, y_test = X[train_split:], y[train_split:]

print(len(X_train), len(y_train), len(X_test), len(y_test))
print()

# Função pra visualizar todas as informações

def plot_predictions(train_data=X_train,
                     train_labels=y_train,
                     test_data=X_test,
                     test_labels=y_test,
                     predictions=None):
    plt.figure(figsize=(10, 7))

    plt.scatter(train_data, train_labels, c="b", s=4, label="Training data")

    plt.scatter(test_data, test_labels, c="g", s=4, label="Testing data")

    if predictions is not None:
        plt.scatter(test_data, predictions, c="r", s=4, label="Predictions")
    
    plt.legend(prop={"size": 15})
    plt.show()

# plot_predictions()

class LinearRegressionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.weights = nn.Parameter(torch.randn(1,
            requires_grad=True, # True é o padrão
            dtype=torch.float # float32 é o padrão
        ))
        
        self.bias = nn.Parameter(torch.randn(1,
            requires_grad=True,
            dtype=torch.float
        ))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor: # "x" é o input
        return self.weights * x + self.bias # Essa é a formula de regressão

# torch.nn -> contem todas as build para graficos computacionais (uma rede neural é considerada um grafico computacional)
# torch.nn.Parameter -> Quais parametros o modelo deveria tentar aprender, normalmente torch.nn vai setar isso automaticamente
# nn.Module -> A classe basica de todos os modulos de rede neural, se você fizer sua rede uma subclasse disso, então reescreva
#              a função forward()
# torch.optim -> Isso ajuda com o "gradient descent"
# def foward() -> todas as subclasses de nn.Module precisam sobrescrever essa função, ela decide o que acontece na proxima computação

# ----------------------------------------------------------------------------------------------------------------------------

# Podemos checar os parametros do modelo usando .parameters()

# Seed aleatoria
torch.manual_seed(42)

# Criar uma instancia do modelo
model_0 = LinearRegressionModel()

# Checar os parametros
print(list(model_0.parameters()))
print()

# Lista nomeada dos parametros
print(model_0.state_dict())
print()

# ------------------------------------------------------------------------------------------

## Criando presivões usando "torch.inference_mode()"

# Agora vamos ver o quão bem o modelo prevê "y_test" baseando-se em "X_test"

# Quando passarmos as informações pelo modelo, ele vai rodar elas pela função "foward()"

# ---

## Criando previsões usando o modelo
with torch.inference_mode():
    y_preds = model_0(X_test)

# Também pode usar:
# with torch.no_grad():
#     y_preds = model_0(X_test)

print(y_preds)
print()

# plot_predictions(predictions=y_preds)

# -------------------------------------------------------------------------------------

## Treinando modelos

# A ideia de "treinar" é pra fazer um modelo mover de parametros aleatorios para parametros conhecidos
# ou em outras palavras de uma má representação de informações para uma melhor representação

# Uma das formas de fazer isso é usar uma "função de perca"

## Coisas que precisamos pra treinar o modelo:

# Função de perca(Loss Function): É uma função que calcula o quão errada são as previsões do modelo em relação com
#                                 outputs ideais, menor é melhor.

# Optmizer: Toma em conta o valor de perca de um modelo e ajusta os parametros desse modelo. (Weight & Bias)

# E especificamente para o pytorch, nós precisamos de um loop de treino e um loop de teste.

# ---

## Configurando uma função de perca(Loss Function)
loss_fn = nn.L1Loss()

## Configurando um optmizer
optmizer = torch.optim.SGD( # <- (stochastic gradient descent)
    params=model_0.parameters(),
    lr=0.01, # <= lr = learning rate (O hiper-parametro mais importante)
)

## Criando um Loop de Treino no Pytorch

# O loop de treino precisa de:
# 1. Rodar o loop na DATA
# 2. Forward Pass (Isso envolve DATA passando pela função "forward()" do modelo) - Também chamado de "forward propagation"
# 3. Calcular a perca "loss" (compara as previsões de forward pass com "truth labels")
# 4. optimizer zero grad
# 5. Loss backward (se move pra trás na rede neural para calcular a "gradiance" de cada parametro do modelo dependendo da "loss" dele)
# 6. Optmizer step (Usa o optimizer para ajustar os parametros do modelo, assim diminuindo a taxa de "loss") -> "gradient descent"

# ---

torch.manual_seed(42)

# Quantidade de loops
epochs = 10

# Monitorar valores:
epoch_count = []
loss_values = []
test_loss_values = []

# Passo 1. Rodar loop na DATA
for epoch in range(epochs):
    # Setar o modelo para modo de treinamento
    model_0.train() # Modo de treino no PyTorch seta todos os parametros que requerem "gradients" para requerirem "gradients"

    # 2. Foward Pass
    y_pred = model_0(X_train)

    # 3. Calcular a "loss" (perca)
    loss = loss_fn(y_pred, y_train)
    print(f"Loss: {loss}")

    # 4. Optmizer zero grad
    optmizer.zero_grad()

    # 5. Loss Backward
    loss.backward()

    # 6. Optimzer Step (Faz o "gradient descent")
    optmizer.step() # Por padrão as mudanças que o optmizer faz vão acumular durante o loop, então temos que zerar ela no passo 4 do loop.

    # Testando...
    model_0.eval() # Desliga configurações que o modelo não precisa para ser testado
    with torch.inference_mode(): # Desliga o "gradient tracking" e mais outras coisas
    # - with torch.no_grad(): # Versão antiga de fazer isso ^   
        # 2. Foward pass
        test_pred = model_0(X_test)

        # 3. Calcular a perca (loss)
        test_loss = loss_fn(test_pred, y_test)
    
    # Prints
    if epoch % 10 == 0:
        epoch_count.append(epoch)
        loss_values.append(loss)
        test_loss_values.append(test_loss)
        print(f"Epoch: {epoch} | Loss: {loss} | Test Loss: {test_loss} ")
        print(model_0.state_dict())
        print()

print()

# Plot the loss

plt.plot(epoch_count, np.array(torch.tensor(loss_values).numpy()), label="Train Loss")
plt.plot(epoch_count, test_loss_values, label="Test Loss")
plt.title("Training and test loss curves")
plt.ylabel("Loss")
plt.xlabel("Epochs")
plt.legend()
# plt.show()

# --------------------------------------------------------------------------

## Salvando informações de um modelo

# Existem 3 metodos principais para salvar e carregar modelos no PyTorch

# 1. "torch.save()" - Serve para salvar um objeto PyTorch no formato Pickle (Biblioteca de salvamento)
# 2. "torch.load()" - Serve pra carregar um objeto PyTorch Salvo
# 3. "torch.nn.Module.load_state_dict()" - Serve pra carregar um "state dictionary" de um modelo
# ^ Salva o model_0.state_dict()

# Salvando:
# torch.save(model.state_dict(), PATH)

# Carregando:
# model = TheModelClass(*args, **kwargs)
# model.load_state_dict(torch.load(PATH))
# model.eval()

## Outra forma de salvar/carregar é fazer isso com o modelo inteiro

# Salvando:
# torch.save(model, PATH)

# Carregando:
# model = torch.load(PATH)
# model.eval()

## Salvando na pratica:

# 1. Criando o diretorio
MODEL_PATH = Path("models")
MODEL_PATH.mkdir(parents=True, exist_ok=True)

# 2. Criando o "Save Path"
MODEL_NAME = "01_Pytorch_Model_0.pth"
MODEL_SAVE_PATH = MODEL_PATH / MODEL_NAME

# 3. Salvar o state_dict() do modelo
torch.save(
    obj=model_0.state_dict(),
    f=MODEL_SAVE_PATH
   )

## Carregando na pratica:

# Salvamos o "state_dict" do modelo, então para carregar nós criamos uma nova instancia do modelo e carregamos o "state_dict" nele.
loaded_model_0 = LinearRegressionModel()

# Carregar o "state_dict" salvo do model_0 (Isso vai atualizar a nova instancia com os parametros do "state_dict" salvo)
loaded_model_0.load_state_dict(torch.load(f=MODEL_SAVE_PATH))

## Vamos testar o modelo carregado

loaded_model_0.eval()
with torch.inference_mode():
    loaded_model_preds = loaded_model_0(X_test)

model_0.eval()
with torch.inference_mode():
    y_preds = model_0(X_test)

print()
print(y_preds == loaded_model_preds)