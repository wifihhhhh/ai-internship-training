import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 从当前文件往上两层，找到项目根目录。
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def build_real_model(
        *,
        max_retries: int = 1,
        max_tokens: 1024,
) -> ChatOpenAI:
    """读取项目配置，创建真实千问客户端。"""
    # 本地学习项目以 .env 为准，方便修改配置后重新加载。
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
    base_url = os.getenv("QWEN_BASE_URL", "").strip()
    model_name = os.getenv("QWEN_MODEL", "qwen-plus").strip()
    
    if not api_key:
        raise ValueError("缺少 DASHSCOPE_API_KEY，请检查项目根目录的 .env")

    if not base_url:
        raise ValueError("缺少 QWEN_BASE_URL，请检查 .env")

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        timeout=30,
        max_retries=max_retries,
        max_tokens=max_tokens,
        use_responses_api=False,
        # 千问扩展参数：本周使用非思考模式完成基础练习。
        extra_body={"enable_thinking": False},
    )
