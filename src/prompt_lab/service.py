from datetime import date

from src.prompt_lab.client import LLMClient
from src.prompt_lab.parsing import parse_task_extraction
from src.prompt_lab.prompts import build_task_extraction_prompt
from src.prompt_lab.schemas import TaskExtraction

def extract_task(
        user_input: str,
        llm_client: LLMClient,
) -> TaskExtraction:
    """调用模型，再校验其结构化输出"""
    messages = build_task_extraction_prompt(
        user_input=user_input,
        today=date.today(),
    )

    raw_output = llm_client.invoke(messages)

    # 无论模型是否“自称返回 JSON”，都必须进入解析和验证层。
    return parse_task_extraction(raw_output)