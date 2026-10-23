from src.report_lab.retry import should_retry


def test_validation_error_is_not_retried() -> None:
    assert should_retry(ValueError("invalid output")) is False

def test_programming_error_is_not_retried() -> None:
    assert should_retry(TypeError("wrong type")) is False