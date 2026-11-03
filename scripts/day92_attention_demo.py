"""亲手计算注意力"""

from math import sqrt

import torch


def main() -> None:
    torch.manual_seed(42)

    # 3个位置，每个位置4维表示
    x = torch.randn(3, 4)

    q = x
    k = x
    v = x

    scores = q @ k.T / sqrt(k.shape[-1])
    weights = torch.softmax(scores, dim=-1)
    output = weights @ v

    print("注意力权重：")
    print(weights)
    print("每行权重之和：")
    print(weights.sum(dim=-1))
    print("输出形状：", output.shape)

if __name__ == "__main__":
    main()