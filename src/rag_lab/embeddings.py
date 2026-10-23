import os

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from openai import OpenAI

from src.rag_lab.documents import PROJECT_ROOT


class QwenEmbeddings(Embeddings):
    """通过百炼兼容接口实现 LangChain 向量接口"""

    def __init__(self) -> None:
        load_dotenv(PROJECT_ROOT / ".env", override=True)

        api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()

        base_url = (
            os.getenv("QWEN_EMBED_BASE_URL")
            or os.getenv("QWEN_BASE_URL")
            or ""
        ).strip()

        if not api_key or not base_url:
            raise ValueError("缺少百炼密钥或向量接口地址")

        self.model = os.getenv(
            "QWEN_EMBED_MODEL", "text-embedding-v4"
        )

        self.dimensions = int(
            os.getenv("QWEN_EMBED_DIMENSIONS", "1024")
        )

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30,
            max_retries=1,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors = []

        # text-embedding-v4 每批最多 10 条。
        for start in range(0, len(texts), 10):
            batch = texts[start:start+10]

            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
                dimensions=self.dimensions,
                encoding_format="float",
            )

            items = sorted(response.data, key=lambda item: item.index)

            if len(items) != len(batch):
                raise RuntimeError("向量数量与输入数量不一致")

            for item in items:
                if len(item.embedding) != self.dimensions:
                    raise RuntimeError("向量维度与配置不一致")

                vectors.append(item.embedding)

        return vectors

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]