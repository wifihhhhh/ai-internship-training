"""用 TensorFlow 完成同一数字任务"""

import json
from pathlib import Path

import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score

from src.training_lab.digits_data import load_splits


ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    tf.keras.utils.set_random_seed(42)

    output = ROOT / "data" / "training" / "tensorflow_digits"
    output.mkdir(parents=True, exist_ok=False)

    splits = load_splits()
    x_train, y_train = splits["train"]
    x_val, y_val = splits["validation"]
    x_test, y_test = splits["test"]

    model = tf.keras.Sequential([
        tf.keras.Input(shape=(64,)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dropout(0.1),
        tf.keras.layers.Dense(10),
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    history = model.fit(
        x_train,
        y_train,
        validation_data=(x_val, y_val),
        epochs=20,
        batch_size=64,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=4, # 耐心值：连续 4 个 epoch，被监控的指标没有变好，就停止训练。
                restore_best_weights=True,
            ),
        ],
        verbose=2, # 控制训练日志打印模式（0：安静模式，1：进度条模式，2：每个 epoch 打印一行日志）
    )

    predictions = model.predict(
        x_test, verbose=0
    ).argmax(axis=1)

    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
    }

    model.save(output / "best.keras")

    (output / "history.json").write_text(
        json.dumps(history.history, indent=2),
        encoding="utf-8",
    )

    (output / "test_metrics.json").write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(metrics)

if __name__ == "__main__":
    main()