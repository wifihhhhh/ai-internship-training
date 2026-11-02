import torch


def main() -> None:
    x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)

    loss = (x ** 2).sum()
    loss.backward()

    print("x: ", x)
    print("loss: ", loss.item())
    print("梯度: ", x.grad)

if __name__ == "__main__":
    main()