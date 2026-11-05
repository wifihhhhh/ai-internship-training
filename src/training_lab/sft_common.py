import json


MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"

SYSTEM = (
    "把用户输入转换为任务JSON。"
    "字段是intent、title、priority、needs_clarification。"
    "intent只能是create_task、query_task、other。"
    "优先级1高2中3低，未说明为null。"
    "创建内容不明确时需要澄清。"
    "查询或闲聊的title和priority为null。"
    "只输出JSON。"
)

def load_rows(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

def prompt_messages(text):
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": text},
    ]