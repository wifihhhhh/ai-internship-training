from uuid import uuid4

import pytest

from src.report_lab.export import save_once


def test_repeated_export_reuses_same_file(tmp_path) -> None:
    task_id = uuid4().hex
    text = " # 学习简报\n\n需要让缓存失效。\n"

    first = save_once(task_id, text, tmp_path)
    second = save_once(task_id, text, tmp_path)

    assert first == second
    assert first.read_text(encoding="utf-8") == text
    assert len(list(tmp_path.glob("*.md"))) == 1

def test_invalid_task_id_is_rejected(tmp_path) -> None:
    with pytest.raises(ValueError):
        save_once("../outside", "内容", tmp_path)