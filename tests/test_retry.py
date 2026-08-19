import pytest

from pix_webhook_toolkit.retry import RetryPolicy, with_retry


def test_returns_value_without_retrying_on_success():
    calls = {"n": 0}

    @with_retry(RetryPolicy(max_attempts=3, base_delay_seconds=0))
    def flaky():
        calls["n"] += 1
        return "ok"

    assert flaky() == "ok"
    assert calls["n"] == 1


def test_retries_until_success():
    calls = {"n": 0}

    @with_retry(RetryPolicy(max_attempts=5, base_delay_seconds=0))
    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return "recovered"

    assert flaky() == "recovered"
    assert calls["n"] == 3


def test_raises_after_exhausting_attempts():
    calls = {"n": 0}

    @with_retry(RetryPolicy(max_attempts=2, base_delay_seconds=0))
    def always_fails():
        calls["n"] += 1
        raise ValueError("boom")

    with pytest.raises(ValueError):
        always_fails()
    assert calls["n"] == 2
