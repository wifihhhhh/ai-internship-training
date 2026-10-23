from hashlib import sha256
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"

def load_documents() -> list[Document]:
    """读取知识目录中的 Markdown 文件"""
    documents = []

    for path in sorted(KNOWLEDGE_DIR.rglob("*.md")):
        text = path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={"source": path.relative_to(KNOWLEDGE_DIR).as_posix()},
            )
        )

    return documents

def split_documents(documents: list[Document]):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100,
        # 优先按段落和中文标点分割
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    )

    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        # 来源和内容共同决定 ID，便于识别重复导入。
        identity = (
            chunk.metadata["source"] + "\n" + chunk.page_content
        )

        chunk.metadata["chunk_id"] = sha256(
            identity.encode("utf-8")
        ).hexdigest()

    return chunks