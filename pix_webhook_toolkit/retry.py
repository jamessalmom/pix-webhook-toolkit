"""Exponential backoff retry decorator with jitter.

Used to make outbound calls to partner/ERP APIs resilient to transient
network failures without hammering the remote service.
"""

from __future__ import annotations

import functools
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

logger = logging.getLogger("pix_webhook_toolkit.retry")

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """Configuration for the exponential backoff strategy."""

    max_attempts: int = 5
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 20.0
    jitter_seconds: float = 0.25
    retry_on: tuple[type[BaseException], ...] = (Exception,)

    def delay_for(self, attempt: int) -> float:
        """Delay (in seconds) before the given attempt number (1-indexed)."""
        exp_delay = self.base_delay_seconds * (2 ** (attempt - 1))
        capped = min(exp_delay, self.max_delay_seconds)
        return capped + random.uniform(0, self.jitter_seconds)


def with_retry(policy: RetryPolicy | None = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that retries a function according to ``policy``.

    Logs each failed attempt (structured, so it can be piped into a log
    aggregator) and re-raises the last exception once attempts are exhausted.
    """

    policy = policy or RetryPolicy()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exc: BaseException | None = None
            for attempt in range(1, policy.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except policy.retry_on as exc:  # type: ignore[misc]
                    last_exc = exc
                    if attempt == policy.max_attempts:
                        logger.error(
                            "retry_exhausted",
                            extra={
                                "function": func.__qualname__,
                                "attempt": attempt,
                                "error": str(exc),
                            },
                        )
                        raise
                    delay = policy.delay_for(attempt)
                    logger.warning(
                        "retry_attempt_failed",
                        extra={
                            "function": func.__qualname__,
                            "attempt": attempt,
                            "next_delay_seconds": round(delay, 3),
                            "error": str(exc),
                        },
                    )
                    time.sleep(delay)
            # Unreachable, but keeps type checkers happy.
            assert last_exc is not None
            raise last_exc

        return wrapper

    return decorator
