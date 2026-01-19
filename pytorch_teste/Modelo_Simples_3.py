import torch
import torch.nn as nn
import torch.optim as optim
import time

alfabeto = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Entradas: posições (0 a 25)
X = torch.arange(26).float().unsqueeze(1)
# X.shape = (26, 1)

# Saidas: classes (0 a 25)
y = torch.arange(26)
# y.shape = (26)

class ModeloAlfabeto(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(1, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, 26)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

model = ModeloAlfabeto()

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

epochs = 1000

for epoch in range(epochs):
    optimizer.zero_grad()
    
    outputs = model(X)
    loss = criterion(outputs, y)

    loss.backward()
    optimizer.step()

    print(f"\n===== Epoch: {epoch} =====")
    print(f"Loss total: {loss.item():.4f}\n")

    for i in range(26):
        probs = torch.softmax(outputs[i], dim=0)
        chute = torch.argmax(probs).item()

        letra_correta = alfabeto[i]
        letra_chute = alfabeto[chute]

        acertou = "V" if chute == i else "F"

        print(
            f"Entrada {i:2d} | "
            f"Chute: {letra_chute} | "
            f"Correto: {letra_correta} | "
            f"Confiança: {probs[chute].item():.2f} | "
            f"{acertou}"
        )
    
    # input(f"Pressione ENTER para continuar para o proximo epoch")