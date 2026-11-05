import argparse
import json
import random
from pathlib import Path

import torch
from huggingface_hub import model_info
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.training_lab.sft_common import MODEL_ID, load_rows, prompt_messages


ROOT = Path(__file__).resolve().parents[1]

def encode_row(tokenizer, row):
    messages = prompt_messages(row["input"])

    prefix = tokenizer.apply_chat_template(
        messages, 
        tokenize=True, 
        add_generation_prompt=True,
    )

    full = tokenizer.apply_chat_template(
        messages + [{
            "role": "assistant",
            "content": json.dumps(
                row["target"], 
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        }],
        tokenize=True,
        add_generation_prompt=False,
    )

    if full[:len(prefix)] != prefix:
        raise ValueError("聊天模板前缀不匹配，不能正确屏蔽提示词")

    if len(full) > 256:
        raise ValueError("样例超过256 Token，请先缩短样例")

    labels = [-100] * len(prefix) + full[len(prefix):]

    if all(value == -100 for value in labels):
        raise ValueError("样例没有可训练的回答Token")

    return {
        "input_ids": torch.tensor(full).unsqueeze(0),
        "attention_mask": torch.ones(
            1, len(full), dtype=torch.long
        ),
        "labels": torch.tensor(labels).unsqueeze(0),
    }

def validation_loss(model, rows):
    model.eval()
    total = 0.0
    count = 0

    with torch.inference_mode():
        for batch in rows:
            token_count = (
                batch["labels"] != -100
            ).sum().item()

            loss = model(**batch).loss.item()
            total += loss * token_count
            count += token_count

    return total / count

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="lora_smoke")
    parser.add_argument("--steps", type=int, default=5)
    args = parser.parse_args()

    if args.steps < 1:
        raise ValueError("steps必须大于0")

    if (
        not args.run
        or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in args.run)
    ):
        raise ValueError("run名称不合法")

    torch.manual_seed(42)
    torch.set_num_threads(4)
    random.seed(42)

    output = ROOT / "data" / "training" / args.run
    output.mkdir(parents=True, exist_ok=False)

    # 记录实际模型版本，后续基础模型对比使用同一版本。
    revision = model_info(MODEL_ID).sha

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_ID, revision=revision
    )

    base = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        revision=revision,
        torch_dtype=torch.float32,
    )
    base.config.use_cache = False

    model = get_peft_model(
        base,
        LoraConfig(
            task_type="CAUSAL_LM",
            r=4, # LoRA 的秩 rank。控制可训练矩阵的维度。r 越小，参数量越少、越不容易过拟合，但表达能力弱。
            lora_alpha=8, # 缩放系数。缩放 = lora_alpha / r
            lora_dropout=0.05,
            target_modules=["q_proj", "v_proj"],
        ),
    )

    model.print_trainable_parameters()

    train_rows = [
        encode_row(tokenizer, row)
        for row in load_rows(ROOT / "data/sft/train.jsonl")
    ]

    val_rows = [
        encode_row(tokenizer, row)
        for row in load_rows(ROOT / "data/sft/validation.jsonl")
    ]

    optimizer = torch.optim.AdamW(
        [
            parameter
            for parameter in model.parameters()
            if parameter.requires_grad
        ],
        lr=0.0002,
    )

    best_val = float("inf")
    history = []

    for step in range(1, args.steps + 1):
        model.train()
        batch = random.choice(train_rows)

        optimizer.zero_grad()
        loss = model(**batch).loss
        loss.backward()
        optimizer.step()

        row = {
            "step": step,
            "train_loss": loss.item(),
        }
        print(row, flush=True)

        if step % 5 == 0 or step == args.steps:
            val_loss = validation_loss(model, val_rows)
            row["val_loss"] = val_loss

            print("validation loss: ", val_loss, flush=True)

            if val_loss < best_val:
                best_val = val_loss
                model.save_pretrained(output / "adapter")
                tokenizer.save_pretrained(output / "adapter")

        history.append(row)

    (output / "history.json").write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )

    (output / "metadata.json").write_text(
        json.dumps({
            "model_id": MODEL_ID,
            "revision": revision,
            "steps": args.steps,
            "rank": 4,
            "best_val_loss": best_val,
        }, indent=2),
        encoding="utf-8",
    )

    print("Adapter保存目录：", output / "adapter")

if __name__ == "__main__":
    main()