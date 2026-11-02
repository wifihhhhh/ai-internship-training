"""写模型与训练循环"""

from torch import nn


class DigitsMLP(nn.Module):
    def __init__(self, hidden: int = 64) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(64, hidden), # 输入维度=64
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, 10), # 输出维度（即类别数）=10
        )

    def forward(self, x):
        return self.network(x)