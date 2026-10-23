from langchain_core.documents import Document

from src.rag_lab.store import get_store


class KnowledgeBaseEmptyError(RuntimeError):
    pass

def retrieve(
        question: str, 
        k: int = 3,
) -> list[tuple[Document, float]]:
    store = get_store()

    if not store.get(limit=1)["ids"]:
        raise KnowledgeBaseEmptyError("知识库为空，请先导入文档")

    return store.similarity_search_with_score(question, k=k,)
