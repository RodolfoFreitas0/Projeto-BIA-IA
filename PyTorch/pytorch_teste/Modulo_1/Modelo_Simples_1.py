import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# -----------------------------
# Dados (simples, só para rodar)
# -----------------------------
weight = 0.7
bias = 0.3

X = torch.arange(0, 1, 0.02).unsqueeze(1)
y = weight * X + bias

train_split = int(0.8 * len(X))
X_train, y_train = X[:train_split], y[:train_split]
X_test, y_test = X[train_split:], y[train_split:]


# -----------------------------
# Função de plot
# -----------------------------
def plot_predictions(train_data,
                     train_labels,
                     test_data,
                     test_labels,
                     predictions=None):
    plt.figure(figsize=(10, 7))
    plt.scatter(train_data, train_labels, s=10, label="Treino")
    plt.scatter(test_data, test_labels, s=10, label="Teste")

    if predictions is not None:
        plt.scatter(test_data, predictions, s=10, label="Previsões")

    plt.legend()
    plt.show()


# -----------------------------
# Modelo
# -----------------------------
class LinearRegressionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.weights = nn.Parameter(torch.randn(1))
        self.bias = nn.Parameter(torch.randn(1))

    def forward(self, x):
        return self.weights * x + self.bias


# -----------------------------
# Treinamento
# -----------------------------
torch.manual_seed(42)
model = LinearRegressionModel()

loss_fn = nn.L1Loss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

epochs = 100
for epoch in range(epochs):
    model.train()

    y_pred = model(X_train)
    loss = loss_fn(y_pred, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    weight_atual = model.weights.item()
    bias_atual = model.bias.item()

    print(
        f"Epoch [{epoch+1}/{epochs}] | "
        f"Loss: {loss.item():.6f} | "
        f"Weight: {weight_atual:.4f} | "
        f"Bias: {bias_atual:.4f}"
    )
    print()


# -----------------------------
# Inferência + gráfico
# -----------------------------
model.eval()
with torch.inference_mode():
    y_preds = model(X_test)

plot_predictions(
    train_data=X_train,
    train_labels=y_train,
    test_data=X_test,
    test_labels=y_test,
    predictions=y_preds
)
