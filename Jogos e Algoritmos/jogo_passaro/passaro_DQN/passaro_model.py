import torch
import torch.nn as nn

class DQN(nn.Module):
    def __init__(self, input_size=5, output_size=2):
        super().__init__()
        
        self.net = nn.Sequential(
            nn.Linear(input_size, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_size)
        )

    def forward(self, x):
        return self.net(x)