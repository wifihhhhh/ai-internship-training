import argparse
import json
from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

from src.training_lab.digits_data import load_splits
from src.training_lab.digits_model import DigitsMLP


ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    args = parser.parse_args()

    directory = ROOT / "data" / "training" / args.run

    config = json.loads(
        (directory / "config.json").read_text(encoding="utf-8")
    )

    model = DigitsMLP(hidden=config["hidden"])

    # 只加载自己生成并信任的权重文件。
    model.load_state_dict(
        torch.load(
            directory / "best.pt", 
            map_location="cpu",
            weight_only=True,
        )
    )
    model.eval()

    x, y = load_splits()["test"]

    with torch.inference_mode():
        predictions = model(
            torch.from_numpy(x)
        ).argmax(dim=1).numpy()

    metrics = {
        "accuracy": float(accuracy_score(y, predictions)),
        "f1": float(f1_score(y, predictions, average="macro")),
        "confusion_matrix": confusion_matrix(y, predictions).tolist(),
    }

    print(json.dumps(metrics, indent=2))

    wrong = [
        (index, int(actual), int(predicted))
        for index, (actual, predicted) 
        in enumerate(zip(y, predictions))
        if actual != predicted
    ]

    print("错误样例：", wrong[:10])

if __name__ == "__main__":
    main()