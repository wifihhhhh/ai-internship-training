def normalize_title(title: str) -> str:
    """删除首尾空格，并将每个单词首字母大写。"""
    return title.strip().title()