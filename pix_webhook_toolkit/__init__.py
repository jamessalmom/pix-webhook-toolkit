"""pix_webhook_toolkit

Small toolkit for building resilient PIX-style webhook receivers and
outbound notifiers: HMAC signature verification, idempotency handling,
and an exponential-backoff HTTP client for calling partner APIs.

This is a generic, educational implementation inspired by common patterns
used when integrating with instant-payment (PIX/SPI/DICT-like) systems.
It does not implement any proprietary or confidential specification.
"""

from .client import ResilientClient
from .retry import RetryPolicy, with_retry
from .signature import sign_payload, verify_signature

__all__ = [
    "ResilientClient",
    "RetryPolicy",
    "sign_payload",
    "verify_signature",
    "with_retry",
]

__version__ = "0.1.0"
