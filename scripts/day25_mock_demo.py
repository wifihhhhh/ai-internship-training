from src.prompt_lab.client import MockLLMClient
from src.prompt_lab.service import extract_task

result = extract_task(
    user_input="明天前完成 FastAPI 测试，优先级最高",
    llm_client=MockLLMClient(),
)

print(result.model_dump_json(indent=2))