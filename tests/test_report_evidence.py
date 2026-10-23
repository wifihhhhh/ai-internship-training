import pytest

from src.report_lab.helpers import validate_brief
from src.report_lab.schemas import Brief


EVIDENCE = [{
    "chunk_id": "known",
    "source": "backend.md",
    "text": "修改任务后，需要让相关缓存失效。",
}]

def make_brief(chunk_id: str, quote: str) -> Brief:
    return Brief(
        title="缓存简报",
        body="修改任务后要处理相关缓存。",
        supported=True,
        citations=[{
            "chunk_id": chunk_id,
            "quote": quote,
        }],
    )

def test_valid_quote_passes() -> None:
    """合法引用应该校验通过。"""
    validate_brief(
        make_brief("known", "需要让相关缓存失效"),
        EVIDENCE,
    )

def test_unknown_suorce_is_rejected() -> None:
    """chunk_id 不存在（来源未知），应该拒绝，抛出异常。"""
    with pytest.raises(ValueError):
        validate_brief(
            make_brief("invented", "需要让相关缓存失效"),
            EVIDENCE,
        )

def test_invented_quote_is_rejected() -> None:
    """chunk_id 是对的，但是引用的 quote 文本是编造的，也要拒绝。"""
    with pytest.raises(ValueError):
            validate_brief(
                make_brief("known", "Redis永远不会出现旧数据"),
                EVIDENCE,
            )