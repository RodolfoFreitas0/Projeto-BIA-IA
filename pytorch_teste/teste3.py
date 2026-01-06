import torch
print(torch.cuda.is_available())
print(f"GPU: {torch.cuda.get_device_name(0)}")