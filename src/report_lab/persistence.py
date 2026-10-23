from contextlib import contextmanager
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

from src.report_lab.graph import build_graph


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_FILE = PROJECT_ROOT / "data" / "report_checkpoints.sqlite"

@contextmanager
def open_graph():
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 连接必须在图执行期间保持打开。
    with SqliteSaver.from_conn_string(
        str(CHECKPOINT_FILE)
    ) as saver:
        saver.setup()
        yield build_graph(checkpointer=saver)