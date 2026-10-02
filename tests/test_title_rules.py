from src.title_rules import normalize_title


def test_normalize_title_removes_extra_spaces() -> None:
    assert normalize_title("  learn   Git  ") == "learn Git"