import torch

x = torch.tensor(2.0, requires_grad=True)
y = x**2 + 3*x
y.backward()

"""
y = x² + 3x

dy/dx = 2x + 3

x = 2

2*2 + 3 = 7
"""

print(f"x.grad: {x.grad}")