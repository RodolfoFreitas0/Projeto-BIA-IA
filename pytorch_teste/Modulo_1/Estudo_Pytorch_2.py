import torch
import matplotlib.pyplot as plt

from torch import nn
from pathlib import Path

# Codigo para usar a GPU caso esteja disponivel
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Dispositivo atual: {device}")

# Criando dados usando a fórmula de regressão linear
weight = 0.7
bias = 0.3

# Criar intervalo de valores
start = 0
end = 1
step = 0.02

# Criar o X e y
X = torch.arange(start, end, step).unsqueeze(dim=1) # Sem esse unsqueeze, erros podem acontecer
y = weight * X + bias
print(f"{X[:10]} \n \n {y[:10]}")
print()

# Dividir os dados
train_split = int(0.8 * len(X))
X_train, y_train = X[:train_split], y[:train_split]
X_test, y_test = X[train_split:], y[train_split:]
print(len(X_train), len(y_train), len(X_test), len(y_test))
print()


plt.ion()

# Função que cria o grafico
def plot_predictions(train_data, train_labels, test_data, test_labels, predictions, epoch):
    plt.cla()
    plt.scatter(train_data, train_labels, s=8, label="Training data")
    plt.scatter(test_data, test_labels, s=8, label="Testing data")
    plt.scatter(test_data, predictions, s=8, label="Predictions")
    plt.title(f"Epoch {epoch}")
    plt.legend()
    plt.pause(0.01)

# Mostrar o grafico
# plot_predictions(X_train, y_train, X_test, y_test)

# Criar o modelo linear (Sempre transforma-lo numa subclasse de nn.Module)
class LinearRegressionModuleV2(nn.Module):
    def __init__(self):
        super().__init__()
        # Vamos usar nn.Linear() para criar os parametros do modelo (Fizemos manualmente antes)
        self.linear_layer = nn.Linear(
            in_features=1, # Para cada 1 input X
            out_features=1 # Teremos 1 output y
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear_layer(x) # Isso faz a mesma coisa que return self.weights * x + self.bias do model_0

# Setar a seed manual
torch.manual_seed(42)
model_1 = LinearRegressionModuleV2()

print(f"{model_1} \n \n {model_1.state_dict()}")
print()

# setar o modelo para usar a GPU
model_1.to(device)
print(next(model_1.parameters()).device)

### Treinamento

# Loss Function
loss_fn = nn.L1Loss()

# Optmizer
optimizer = torch.optim.SGD(
    params=model_1.parameters(),
    lr=0.001
    )

epochs = 1500

# Colocar a data no Device correto
X_train = X_train.to(device)
y_train = y_train.to(device)
X_test = X_test.to(device)
y_test = y_test.to(device)

for epoch in range(epochs):
    model_1.train()

    y_preds = model_1(X_train)

    loss = loss_fn(y_preds, y_train)

    optimizer.zero_grad()

    loss.backward()

    optimizer.step()

    # Testes
    model_1.eval()
    with torch.inference_mode():
        test_pred = model_1(X_test)
        
        test_loss = loss_fn(test_pred, y_test)

    if epoch % 10 == 0:
        print(f"Epoch: {epoch} | Loss: {loss} | Test Loss: {test_loss}")

        plot_predictions(
            X_train.cpu(),
            y_train.cpu(),
            X_test.cpu(),
            y_test.cpu(),
            test_pred.cpu(),
            epoch
        )

print()
print(model_1.state_dict())
print()

plt.ioff()
plt.show()

## Salvar e carregar o modelo

# Salvando

MODEL_PATH = Path("models")
MODEL_PATH.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "02_Pytorch_Model_1.pth"
MODEL_SAVE_PATH = MODEL_PATH / MODEL_NAME

torch.save(
    obj=model_1.state_dict(),
    f=MODEL_SAVE_PATH
)

# Carregando

loaded_model_1 = LinearRegressionModuleV2()
loaded_model_1.load_state_dict(torch.load(f=MODEL_SAVE_PATH))

loaded_model_1.to(device)

# Testando

loaded_model_1.eval()
with torch.inference_mode():
    loaded_model_1_preds = loaded_model_1(X_test)

model_1.eval()
with torch.inference_mode():
    y_preds = model_1(X_test)

print(y_preds == loaded_model_1_preds)