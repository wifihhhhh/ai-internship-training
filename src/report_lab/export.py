from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "exports"

def render_report(state: dict) -> str:
    draft = state["draft"]
    evidence = {
        item["chunk_id"]: item
        for item in state["evidence"]
    }

    lines = [
        f"# {draft['title']}",
        "",
        draft["body"],
        "",
        "## 引用",
        "",
    ]

    for citation in draft["citations"]:
        item = evidence[citation["chunk_id"]]
        lines.append(
            f"- source: {item['source']}\n"
            f"  原文：{citation['quote']}"
        )

    return "\n".join(lines) + "\n"

def report_digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()

def save_once(task_id: str, text: str, directory=None) -> Path:
    target_dir = Path(directory) if directory else EXPORT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    # 文件名来自有效 UUID 和内容摘要，不接受用户提供的路径。
    safe_id = UUID(task_id).hex
    digest = report_digest(text)

    target = target_dir / f"{safe_id}-{digest[:12]}.md"

    if target.exists():
        if target.read_text(encoding="utf-8") != text:
            raise ValueError("已存在文件内容不一致")
        return target

    temporary_path = None

    try:
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target_dir,
            delete=False,
        ) as temporary:
            temporary.write(text)
            temporary_path = Path(temporary.name)

        # 完整写好后再替换到目标文件，减少半截报告。
        temporary_path.replace(target)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return target