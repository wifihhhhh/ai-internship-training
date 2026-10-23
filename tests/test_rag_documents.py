from langchain_core.documents import Document

from src.rag_lab.documents import split_documents


def test_chunk_keeps_source_and_stable_id() -> None:
    documents = [
        Document(
            page_content="Redis用于缓存。修改任务后需要让缓存失效。",
            metadata={"source": "example.md"},
        )
    ]

    first = split_documents(documents)
    second = split_documents(documents)

    assert first[0].metadata["source"] == "example.md"
    assert (
        first[0].metadata["chunk_id"] == second[0].metadata["chunk_id"]
    )

def test_long_documents_is_split() -> None:
    documents = [
        Document(
            page_content="这是一段学习笔记。" * 200,
            metadata={"source": "long.md"},
        )
    ]

    chunks = split_documents(documents)

    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 600 for chunk in chunks)