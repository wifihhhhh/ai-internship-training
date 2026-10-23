from math import sqrt

from src.rag_lab.embeddings import QwenEmbeddings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sqrt(sum(x * x for x in a))
    norm_b = sqrt(sum(y * y for y in b))

    return dot / (norm_a * norm_b)

def main() -> None:
    model = QwenEmbeddings()
    vectors = model.embed_documents([
        "Redis 可以缓存任务列表。",
        "用 Redis 缓存查询结果。",
        "Python 函数名后加括号表示调用。",
    ])

    print("dimensions:", len(vectors[0]))
    print("similar topics:", cosine_similarity(vectors[0], vectors[1]))
    print("unsimilar topics:", cosine_similarity(vectors[0], vectors[2]))

if __name__ == "__main__":
    main()