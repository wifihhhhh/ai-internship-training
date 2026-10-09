from datetime import date

from src.prompt_lab.prompts import build_task_extraction_prompt

messages = build_task_extraction_prompt(
    user_input="明天前完成 FastAPI 测试，优先级最高",
    today=date(2026, 10, 5)
)

for message in messages:
    print(f"\n[{message['role']}]\n{message['content']}")