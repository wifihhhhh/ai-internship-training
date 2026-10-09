import pytest

from src.tool_agent.retry import TransientToolError, run_with_retry

def test_retry_succeeds_after_transient_failure() -> None:
    attempts = 0

    def unstable_operation() -> str:
        nonlocal attempts
        attempts += 1

        if attempts < 2:
            raise TransientToolError("temporary failure")

        return "success"

    result = run_with_retry(
        unstable_operation,
        max_attempts=3
    )

    assert result == "success"
    assert attempts == 2

def test_retry_stops_after_max_attempts() -> None:
    def always_fail() -> str:
        raise TransientToolError("still unavailable")

    with pytest.raises(TransientToolError):
        run_with_retry(
            always_fail,
            max_attempts=2,
        )