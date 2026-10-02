def normalize_title(title: str) -> str:
    """删除多余空格，并将每个单词首字母大写。"""
    return " ".join(title.strip().split()).title()