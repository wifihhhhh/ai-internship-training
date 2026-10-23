from src.rag_lab.documents import load_documents, split_documents


def main() -> None:
    documents = load_documents()
    chunks = split_documents(documents)

    print("文档数量：", len(documents))
    print("切块数量：", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n第 {index} 块")
        print("来源：", chunk.metadata["source"])
        print("字符数：", len(chunk.page_content))
        print(chunk.page_content)

if __name__ == "__main__":
    main()