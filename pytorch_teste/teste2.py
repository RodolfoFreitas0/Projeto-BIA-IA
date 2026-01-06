import torch

data = [1, 2, 3, 4, 5]

tensor = torch.tensor(data)

print(tensor)

print(f"Formato do Tensor: {tensor.shape}")
print(f"Tipo de data do Tensor: {tensor.dtype}")