# pix-webhook-toolkit

Small, dependency-light toolkit for building resilient webhook receivers and
outbound notifiers for instant-payment-style integrations (PIX/SPI-like
flows). Extracted and generalized from patterns used in production fintech
integrations: signature verification, idempotency, and exponential backoff.

> Educational/portfolio project: it implements generic patterns, not any
> bank's proprietary specification.

## Features

- **HMAC signature verification** for inbound webhooks (`signature.py`)
- **Exponential backoff with jitter** for outbound calls (`retry.py`)
- **Resilient HTTP client** with automatic idempotency keys (`client.py`)
- **Flask blueprint** ready to mount as a webhook receiver (`webhook.py`)

## Why this exists

Payment webhooks arrive out of order, sometimes duplicated, and partner APIs
occasionally time out under load. This toolkit packages the small set of
primitives I kept re-implementing on transaction/integration work: verify
first, retry safely, never double-process.

## Quick start

```python
from flask import Flask
from pix_webhook_toolkit.webhook import build_webhook_blueprint

def handle_event(payload: dict) -> None:
    print("received", payload)

app = Flask(__name__)
app.register_blueprint(
    build_webhook_blueprint(secret="change-me", on_event=handle_event),
    url_prefix="/webhooks/pix",
)
```

Calling a partner API with retries + idempotency:

```python
from pix_webhook_toolkit import ResilientClient

client = ResilientClient(base_url="https://partner.example.com")
client.post_json("/v1/transfers", {"amount": 100, "txid": "abc123"})
```

## Development

```bash
pip install -r requirements.txt
pip install pytest ruff
pytest
ruff check .
```

## License

MIT — see [LICENSE](LICENSE).
