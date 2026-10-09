from collections.abc import Callable
from time import sleep
from typing import TypeVar

T = TypeVar("T") # 泛型类型变量,T常作占位符

class TransientToolError(RuntimeError):
    """网络波动、临时不可用等可以重试的错误"""

def run_with_retry(
        operation: Callable[[], T],
        max_attempts: int = 3,
) -> T:
    """只对临时错误重试，其他错误直接抛出"""
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except TransientToolError:
            if attempt == max_attempts:
                raise
            
            # 简单退避：第 1 次失败等 1 秒，第 2 次等 2 秒
            sleep(attempt)

    raise RuntimeError("Unreachable code")
    