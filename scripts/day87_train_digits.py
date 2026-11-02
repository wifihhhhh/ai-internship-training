import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.training_lab.digits_data import load_splits
from src.training_lab.digits_model import DigitsMLP


ROOT = Path(__file__).resolve().parents[1]

def evaluate(model, loader, criterion):
    model.eval()

    total_loss = 0.0
    correct = 0
    count = 0

    with torch.inference_mode():
        for x, y in loader:
            logits = model(x)
            loss = criterion(logits, y)

            total_loss += loss.item() * len(y)
            correct += (logits.argmax(dim=1) == y).sum().item()
            count += len(y)

    return total_loss / count, correct / count

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="digits_baseline")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--hidden", type=int, default=64)
    args = parser.parse_args()

    if (
        not args.run
        or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.run)
    ):
        raise ValueError("run只能包含字母、数字、下划线和短横线")

    if args.epochs < 1 or args.lr <= 0 or args.hidden < 1:
        raise ValueError("训练参数必须为正数")

    output = ROOT / "data" / "training" / args.run
    output.mkdir(parents=True, exist_ok=False)

    torch.manual_seed(42)
    torch.set_num_threads(4)

    splits = load_splits()

    def make_loader(name, shuffle):
        x, y = splits[name]

        return DataLoader(
            TensorDataset(
                torch.from_numpy(x),
                torch.from_numpy(y),
            ),
            batch_size=64,
            shuffle=shuffle,
            num_workers=0,
        )

    train_loader = make_loader("train", True)
    val_loader = make_loader("validation", False)

    model = DigitsMLP(hidden=args.hidden)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=args.lr,
    )

    history = []
    best_val_loss = float("inf")

    for epoch in range(1, args.epochs + 1):
        model.train()
        train_loss = 0.0
        train_count = 0

        for x,y in train_loader:
            optimizer.zero_grad()
            logits = model(x)
            loss = criterion(logits, y)

            loss.backward()
            optimizer.step()

            train_loss += loss.item() * len(y)
            train_count += len(y)

        val_loss, val_accuracy = evaluate(
            model, val_loader, criterion
        )

        row = {
            "epoch": epoch,
            "train_loss": train_loss / train_count,
            "val_loss": val_loss,
            "val_accuracy": val_accuracy,
        }
        history.append(row)

        print(row, flush=True)

        if val_loss < best_val_loss:
            best_val_loss = val_loss

            torch.save(
                model.state_dict(),
                output / "best.pt",
            )

    (output / "history.json").write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )

    (output / "config.json").write_text(
        json.dumps(vars(args), indent=2),
        encoding="utf-8",
    )

    print("结果目录：", output)

if __name__ == "__main__":
    main()