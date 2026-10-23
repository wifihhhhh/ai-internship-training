from langgraph.types import RetryPolicy
from openai import APIConnectionError, APIStatusError


def should_retry(error: Exception) -> bool:
    if isinstance(error, APIConnectionError):
        return True

    if isinstance(error, APIStatusError):
        return (
            error.status_code == 429
            or error.status_code >= 500
        )

    return False

READ_RETRY = RetryPolicy(
    max_attempts=2,
    initial_interval=1.0, # 初始等待间隔
    backoff_factor=2.0, # 退避系数（指数退避）。后续每次等待时间 = 上一次间隔 × backoff_factor
    jitter=True, # 开启（间隔时间）抖动。防止大量请求同时重试造成惊群效应
    retry_on=should_retry,
)