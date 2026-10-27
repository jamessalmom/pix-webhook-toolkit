# pix-webhook-toolkit

A small toolkit for receiving and sending webhooks in instant-payment integrations (PIX/SPI-style flows): signature verification, idempotency keys and retries with exponential backoff. These are the pieces I kept rewriting when working on payment integrations.

> This is a portfolio project. It implements generic patterns, not any bank's or PSP's specification.

## What is included

- `signature.py`: HMAC verification for incoming webhooks.
- `retry.py`: exponential backoff with jitter for outgoing calls.
- `client.py`: an HTTP client that adds an idempotency key to every request and retries safely.
- `webhook.py`: a Flask blueprint ready to mount as the webhook receiver.

## Why

Payment webhooks arrive out of order and sometimes twice, and partner APIs time out under load. The rule the toolkit follows is: verify the signature first, retry only what is safe to retry, and never process the same event twice.

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

Calling a partner API with retries and an idempotency key:

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

MIT, see [LICENSE](LICENSE).
