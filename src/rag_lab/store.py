import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_chroma import Chroma

from src.rag_lab.documents import PROJECT_ROOT
from src.rag_lab.embeddings import QwenEmbeddings


@lru_cache(maxsize=1)
def get_store() -> Chroma:
    load_dotenv(PROJECT_ROOT / ".env", override=True)

    return Chroma(
        collection_name=os.getenv(
            "RAG_COLLECTION", "learning_notes_v1"
        ),
        embedding_function=QwenEmbeddings(),
        persist_directory=str(PROJECT_ROOT / "data" / "chroma"),
    )