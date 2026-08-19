"""A small resilient HTTP client wrapping requests + retry + idempotency keys."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Mapping
from typing import Any

import requests

from .retry import RetryPolicy, with_retry

logger = logging.getLogger("pix_webhook_toolkit.client")


class ResilientClient:
    """Thin wrapper around ``requests`` for calling partner/ERP APIs safely.

    Adds: exponential backoff retries, idempotency-key generation for POSTs,
    and structured logging of every outbound call.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        retry_policy: RetryPolicy | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_policy = retry_policy or RetryPolicy(
            retry_on=(requests.ConnectionError, requests.Timeout)
        )
        self.session = session or requests.Session()

    def post_json(
        self,
        path: str,
        payload: Mapping[str, Any],
        idempotency_key: str | None = None,
        extra_headers: Mapping[str, str] | None = None,
    ) -> requests.Response:
        key = idempotency_key or str(uuid.uuid4())
        headers = {"Idempotency-Key": key, "Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)

        @with_retry(self.retry_policy)
        def _send() -> requests.Response:
            url = f"{self.base_url}{path}"
            logger.info("outbound_request", extra={"url": url, "idempotency_key": key})
            response = self.session.post(
                url, json=dict(payload), headers=headers, timeout=self.timeout_seconds
            )
            response.raise_for_status()
            return response

        return _send()
