from datetime import date

def add_numbers(a: float, b: float) -> dict[str, float]:
    """返回两个数字的和"""
    return {
        "a": a,
        "b": b,
        "result": a + b,
    }

def multiply_numbers(a: float, b: float) -> dict[str, float]:
    """返回两个数字的乘积"""
    return {
        "a": a,
        "b": b,
        "result": a * b,
    }

def get_current_date() -> dict[str, str]:
    """返回程序运行当天的日期"""
    return {
        "date": date.today().isoformat(),
    }