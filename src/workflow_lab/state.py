from typing import TypedDict


class RagState(TypedDict, total=False):
    question: str
    search_query: str

    # 用普通字典保存数据，方便检查状态。
    hits: list[dict]
    result: dict

    attempts: int
    history: list[dict[str, str]]
    