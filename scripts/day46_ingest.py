from src.rag_lab.documents import load_documents, split_documents
from src.rag_lab.store import get_store

def main() -> None:
    chunks = split_documents(load_documents())

    if not chunks:
        raise ValueError("knowledge 目录没有可导入的文档")

    # 相同来源、相同内容只保留一份。
    unique_chunks = {
        chunk.metadata["chunk_id"]: chunk
        for chunk in chunks
    }

    store = get_store()
    existing_ids = set(store.get()["ids"])

    new_chunks = [
        chunk for chunk_id, chunk in unique_chunks.items()
        if chunk_id not in existing_ids
    ]

    if new_chunks:
        store.add_documents(
            documents=new_chunks,
            ids=[
                chunk.metadata["chunk_id"]
                for chunk in new_chunks
            ],
        )

        print("本次新增：", len(new_chunks))
        print("集合总块数：", len(store.get()['ids']))

if __name__ == "__main__":
    main()