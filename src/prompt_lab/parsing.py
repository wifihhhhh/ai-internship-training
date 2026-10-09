import json

from pydantic import ValidationError

from src.prompt_lab.schemas import TaskExtraction

class LLMOutputError(ValueError):
    """模型输出不是符合要求的 JSON 时抛出"""

def parse_task_extraction(raw_output: str)-> TaskExtraction:
    """将模型原始文本转换成经过 Pydantic 校验的对象"""
    try:
        data = json.loads(raw_output)
        return TaskExtraction.model_validate(data)
    except (json.JSONDecodeError, ValidationError) as error:
        raise LLMOutputError("LLM output is not a valid task extraction result") from error