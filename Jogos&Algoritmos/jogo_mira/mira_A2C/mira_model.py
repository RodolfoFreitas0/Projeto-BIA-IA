import torch.nn as nn

class A2C(nn.Module):
    def __init__(self, input_size, output_size):
        super().__init__()

        self.base = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.LayerNorm(64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU()
        )

        self.actor = nn.Sequential(
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, output_size)
        )

        self.critic = nn.Sequential(
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
     
    def forward(self, x):
        features = self.base(x)
        action_logits = self.actor(features)
        state_value = self.critic(features)
        return action_logits, state_value