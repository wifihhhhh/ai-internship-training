"""用真实 Transformer 提取特征并训练分类器"""

import json
from pathlib import Path

import torch
from datasets import load_dataset
from sklearn.metrics import accuracy_score, f1_score
from torch import nn
from transformers import AutoModel, AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "distilbert/distilbert-base-uncased"

def main() -> None:
    torch.manual_seed(42)
    torch.set_num_threads(4)

    output = ROOT / "data" / "training" / "transformer_features"
    output.mkdir(parents=True, exist_ok=False)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    backbone = AutoModel.from_pretrained(MODEL_ID)
    backbone.eval()

    for parameter in backbone.parameters():
        parameter.requires_grad = False

    dataset = load_dataset(
        "cornell-movie-review-data/rotten_tomatoes"
    )

    features = {}
    labels = {}

    sizes = {
        "train": 400,
        "validation": 100,
        "test": 100,
    }

    for split, size in sizes.items():
        rows = dataset[split].shuffle(seed=42).select(range(size))
        batches = []

        for start in range(0, size, 16):
            texts = rows[start : start + 16]["text"]

            inputs = tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=96,
                return_tensors="pt",
            )

            with torch.inference_mode():
                hidden = backbone(**inputs).last_hidden_state

                # 取第一个位置作为分类特征。
                vectors = hidden[:, 0, :]

            batches.append(vectors)

        features[split] = torch.cat(batches)
        labels[split] = torch.tensor(rows["label"])

    # 从推理模式生成的特征复制为普通训练输入。
    features = {
        name: value.clone()
        for name, value in features.items()
    }

    classifier = nn.Linear(backbone.config.hidden_size, 2)
    optimizer = torch.optim.Adam(
        classifier.parameters(), lr=0.01
    )

    criterion = nn.CrossEntropyLoss() # 分类损失函数

    best_loss = float("inf")
    history = []

    for epoch in range(1, 101):
        classifier.train()
        optimizer.zero_grad()

        logits = classifier(features["train"])
        loss = criterion(logits, labels["train"])

        loss.backward()
        optimizer.step()

        classifier.eval()

        with torch.no_grad():
            val_logits = classifier(features["validation"])
            val_loss = criterion(
                val_logits, labels["validation"]
            ).item()

            val_accuracy = (
                val_logits.argmax(dim=1)
                == labels["validation"]
            ).float().mean().item()

        history.append({
            "epoch": epoch,
            "train_loss": loss.item(),
            "val_loss": val_loss,
            "val_accuracy": val_accuracy,
        })

        if val_loss < best_loss:
            best_loss = val_loss
            torch.save(
                classifier.state_dict(),
                output / "classifier.pt",
            )

    classifier.load_state_dict(
        torch.load(
            output / "classifier.pt",
            weights_only=True,
        )
    )

    with torch.no_grad():
        predictions = classifier(
            features["test"]
        ).argmax(dim=1).numpy()

    actual = labels["test"].numpy()

    metrics = {
        "accuracy": float(accuracy_score(actual, predictions)),
        "macro_f1": float(f1_score(actual, predictions, average="macro")),
        "model": MODEL_ID,
        "training_type": "frozen_backbone_linear_head",
    }

    (output / "history.json").write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )
    (output / "test_metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(metrics)

if __name__ == "__main__":
    main()