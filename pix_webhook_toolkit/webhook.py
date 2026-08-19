"""Flask blueprint exposing a webhook receiver endpoint.

Example usage::

    from flask import Flask
    from pix_webhook_toolkit.webhook import build_webhook_blueprint

    app = Flask(__name__)
    app.register_blueprint(
        build_webhook_blueprint(secret="change-me", on_event=my_handler),
        url_prefix="/webhooks/pix",
    )
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from flask import Blueprint, jsonify, request

from .signature import verify_signature

logger = logging.getLogger("pix_webhook_toolkit.webhook")


def build_webhook_blueprint(
    secret: str,
    on_event: Callable[[dict], None],
    signature_header: str = "X-Signature",
) -> Blueprint:
    """Build a Flask blueprint that validates and dispatches webhook events."""

    bp = Blueprint("pix_webhook", __name__)

    @bp.post("")
    def receive() -> tuple:
        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify({"error": "invalid_json"}), 400

        signature = request.headers.get(signature_header, "")
        if not verify_signature(payload, secret, signature):
            logger.warning("webhook_signature_mismatch", extra={"remote_addr": request.remote_addr})
            return jsonify({"error": "invalid_signature"}), 401

        try:
            on_event(payload)
        except Exception:  # pragma: no cover - defensive log, re-raised for the caller to handle
            logger.exception("webhook_handler_failed")
            return jsonify({"error": "processing_failed"}), 500

        return jsonify({"status": "accepted"}), 202

    return bp
