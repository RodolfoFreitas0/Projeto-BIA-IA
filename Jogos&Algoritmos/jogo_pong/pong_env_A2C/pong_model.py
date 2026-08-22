import torch.nn as nn

class A2C(nn.Module):
    def __init__(self):
        super().__init__()

        self.base = nn.Sequential(
            nn.Linear(7, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU()
        )

        self.actor = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 3)
        )

        self.critic = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

     
    def forward(self, x):
        features = self.base(x)
        action_logits = self.actor(features)
        state_value = self.critic(features)
        return action_logits, state_value