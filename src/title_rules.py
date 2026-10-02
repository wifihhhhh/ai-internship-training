def normalize_title(title: str) -> str:
    """删除首尾空格，并压缩中间多余空格。"""
    return " ".join(title.strip().split())