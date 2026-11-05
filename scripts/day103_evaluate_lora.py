import argparse
import json
from contextlib import nullcontext
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.training_lab.sft_common import load_rows, prompt_messages


ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument(
        "--split",
        choices=["validation", "test"],
        default="validation",
    )
    args = parser.parse_args()

    torch.set_num_threads(4) # 计算线程数：单个CPU算子内部并行用

    directory = ROOT / "data" / "training" / args.run
    metadata = json.loads(
        (directory / "metadata.json").read_text(encoding="utf-8")
    )

    tokenizer = AutoTokenizer.from_pretrained(
        directory / "adapter"
    )

    base = AutoModelForCausalLM.from_pretrained(
        metadata["model_id"],
        revision=metadata["revision"], # Hugging Face Transformers 库里的参数，定位这个仓库里某一个固定版本
        torch_dtype=torch.float32
    )

    model = PeftModel.from_pretrained(
        base, directory / "adapter"
    )
    model.eval()

    rows = load_rows(
        ROOT / "data" / "sft" / f"{args.split}.jsonl"
    )

    records = []

    for method in ["baseline", "adapter"]:
        correct = 0
        parsed_count = 0

        context = (
            model.disable_adapter()
            if method == "baseline"
            else nullcontext()
        )

        with context:
            for row in rows:
                text = tokenizer.apply_chat_template(
                    prompt_messages(row["input"]),
                    tokenize=False,
                    add_generation_prompt=True,
                )

                inputs = tokenizer(
                    text,
                    return_tensors="pt",
                    add_special_tokens=False,
                )

                with torch.inference_mode():
                    output = model.generate(
                        **inputs,
                        max_new_tokens=128,
                        do_sample=False,
                        use_cache=True,
                        pad_token_id=tokenizer.eos_token_id,
                    )

                generated = tokenizer.decode(
                    output[0][inputs["input_ids"].shape[1]:],
                    skip_special_tokens=True,
                ).strip()

                try:
                    prediction = json.loads(generated)
                    parsed = True
                    parsed_count += 1
                except json.JSONDecodeError:
                    prediction = None
                    parsed = False

                exact = prediction == row["target"]
                correct += exact

                records.append({
                    "method": method,
                    "input": row["input"],
                    "target": row["target"],
                    "generated": generated,
                    "json_valid": parsed,
                    "exact_match": exact,
                })

                print(method, row["input"], exact, flush=True)

        print(
            method,
            "JSON解析率：", parsed_count / len(rows),
            "完全匹配率：", correct / len(rows),
        )

    (directory / f"{args.split}_results.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

if __name__ == "__main__":
    main()