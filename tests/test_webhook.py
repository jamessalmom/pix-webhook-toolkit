from flask import Flask

from pix_webhook_toolkit.signature import sign_payload
from pix_webhook_toolkit.webhook import build_webhook_blueprint

SECRET = "test-secret"


def make_app(on_event):
    app = Flask(__name__)
    app.register_blueprint(build_webhook_blueprint(SECRET, on_event), url_prefix="/webhooks")
    return app


def test_accepts_valid_signed_payload():
    received = []
    app = make_app(received.append)
    client = app.test_client()

    payload = {"txid": "abc", "amount": 10}
    sig = sign_payload(payload, SECRET)

    resp = client.post("/webhooks", json=payload, headers={"X-Signature": sig})

    assert resp.status_code == 202
    assert received == [payload]


def test_rejects_bad_signature():
    app = make_app(lambda p: None)
    client = app.test_client()

    resp = client.post("/webhooks", json={"txid": "abc"}, headers={"X-Signature": "wrong"})

    assert resp.status_code == 401
