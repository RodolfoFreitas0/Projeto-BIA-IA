import torch
import torch.nn as nn

layer = nn.Linear(2, 1)

# Internamente: y = x1*w1 + x2*w2 + bias

x = torch.tensor([[1., 2.]])
y = layer(x)
print(y)