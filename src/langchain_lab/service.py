from functools import lru_cache

from src.langchain_lab.chains import build_task_extraction_chain
from src.langchain_lab.models import build_real_model

@lru_cache(maxsize=1)
def get_extraction_chain():
    """复用模型客户端和提取链，不缓存用户回答"""
    return build_task_extraction_chain(build_real_model())

def extract_task(message: str):
    chain = get_extraction_chain()
    return chain.invoke({"message": message})