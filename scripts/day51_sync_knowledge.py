from collections import defaultdict

from src.rag_lab.documents import load_documents, split_documents
from src.rag_lab.store import get_store


def main() -> None:
    documents = load_documents()

    if not documents:
        raise ValueError("没有文档，本次不进行同步")

    # 空文件也应清理旧块，因此用文件来源作为同步对象。
    chunks_by_source = defaultdict(dict)

    for document in documents:
        source = document.metadata["source"]

        for chunk in split_documents([document]):
            chunks_by_source[source][chunk.metadata["chunk_id"]] = chunk

    store = get_store()

    for source, current in chunks_by_source.items():
        old_ids = set(
            store.get(where={"source": source})["ids"]
        )

        current_ids = set(current)
        new_ids = current_ids - old_ids
        stale_ids = old_ids - current_ids

        # 先写新内容，成功后再清理旧块。
        if new_ids:
            store.add_documents(
                documents=[current[item] for item in sorted(new_ids)],
                ids=sorted(new_ids),
            )

        if stale_ids:
            store.delete(ids=sorted(stale_ids))

        print(
            source,
            "新增：", len(new_ids),
            "删除旧块：", len(stale_ids),
        )

if __name__ == "__main__":
    main()