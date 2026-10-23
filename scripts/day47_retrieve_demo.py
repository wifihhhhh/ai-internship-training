from src.rag_lab.retrieval import retrieve


def main() -> None:
    question = "修改任务后，为什么任务列表可能还是旧的？"

    for document, distance in retrieve(question, k=3):
        print("\nsource:", document.metadata["source"])
        print("distance:", distance)
        print(document.page_content)

if __name__ == "__main__":
    main()