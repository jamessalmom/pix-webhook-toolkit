"""HMAC-based signature helpers for webhook authenticity checks."""

from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Mapping
from typing import Any


def _canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    """Serialize a payload deterministically so signing is order-independent."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_payload(payload: Mapping[str, Any], secret: str) -> str:
    """Return a hex HMAC-SHA256 signature for ``payload`` using ``secret``."""
    digest = hmac.new(secret.encode("utf-8"), _canonical_bytes(payload), hashlib.sha256)
    return digest.hexdigest()


def verify_signature(payload: Mapping[str, Any], secret: str, signature: str) -> bool:
    """Constant-time comparison between the expected and received signature."""
    expected = sign_payload(payload, secret)
    return hmac.compare_digest(expected, signature)
