import torch
import matplotlib.pyplot as plt

from torch import nn
from pathlib import Path

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Dispositivo atual: {device}")

weight = 0.3
bias = 0.9

start = 0
end = 1
step = 0.02

X = torch.arange(start, end, step).unsqueeze(dim=1)
y = weight * X + bias
print(f"{X[:10]} \n \n {y[:10]}")
print() 

train_split = int(0.8 * len(X))
X_train, y_train = X[:train_split], y[:train_split]
X_test, y_test = X[train_split:], y[train_split:]
print(len(X_train), len(y_train), len(X_test), len(y_test))
print()

plt.ion()

def plot_predictions(train_data, train_labels, test_data, test_labels, predictions, epoch):
    plt.cla()
    plt.scatter(train_data, train_labels, s=8, label="Training data")
    plt.scatter(test_data, test_labels, s=8, label="Testing data")
    plt.scatter(test_data, predictions, s=8, label="Predictions")
    plt.title(f"Epoch {epoch}")
    plt.legend()
    plt.pause(0.01)

class LinearRegressionModuleV2(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear_layer = nn.Linear(
            in_features=1,
            out_features=1
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear_layer(x)

torch.manual_seed(42)
model_2 = LinearRegressionModuleV2()

model_2.to(device)

loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(
    params=model_2.parameters(),
    lr=0.01
)

epochs = 200

X_train = X_train.to(device)
y_train = y_train.to(device)
X_test = X_test.to(device)
y_test = y_test.to(device)

for epoch in range(epochs):
    model_2.train()

    y_preds = model_2(X_train)

    loss = loss_fn(y_preds, y_train)

    optimizer.zero_grad()
    
    loss.backward()

    optimizer.step()

    model_2.eval()
    with torch.inference_mode():
        test_pred = model_2(X_test)

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
print(model_2.state_dict())
print()

plt.ioff()
plt.show()

MODEL_PATH = Path("models")
MODEL_PATH.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "03_Pytorch_Model_2.pth"
MODEL_SAVE_PATH = MODEL_PATH / MODEL_NAME

torch.save(
    obj=model_2.state_dict(),
    f=MODEL_SAVE_PATH
)

loaded_model_2 = LinearRegressionModuleV2()
loaded_model_2.load_state_dict(torch.load(f=MODEL_SAVE_PATH))

loaded_model_2.to(device)

loaded_model_2.eval()
with torch.inference_mode():
    loaded_model_2_preds = loaded_model_2(X_test)

model_2.eval()
with torch.inference_mode():
    y_preds = model_2(X_test)

print(y_preds == loaded_model_2_preds)