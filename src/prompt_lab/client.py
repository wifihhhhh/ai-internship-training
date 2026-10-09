from typing import Protocol

import requests

class LLMClient(Protocol):
    """定义模型客户端的统一接口"""
    def invoke(
        self, 
        messages: list[dict[str, str]],
    ) -> str:
        """返回模型生成的原始文本"""

class MockLLMClient:
    """不调用真实模型，用于本地测试与学习"""
    def invoke(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        # 返回固定结果，让测试不依赖 API Key、网络或模型随机性
        return """{
            "intent": "create_task",
            "title": "完成 FastAPI 测试",
            "priority": 1,
            "due_date": "2026-10-06",
            "needs_clarification": false,
            "clarification_question": null
        }"""

class OpenAICompatibleLLMClient:
    """适用于 OpenAI 兼容 Chat Completions 接口的简化客户端"""
    def __init__(
        self, 
        api_key: str,
        base_url: str,
        model: str
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def invoke(self, messages: list[dict[str, str]]) -> str:
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": messages,
                "temperature": 0,
            },
            timeout=30,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]