from src.title_rules import normalize_title


def test_normalize_title_formats_spaces_and_capitalization() -> None:
    assert normalize_title("  learn   git  ") == "Learn Git"