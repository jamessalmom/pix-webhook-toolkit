from pix_webhook_toolkit.signature import sign_payload, verify_signature


def test_sign_is_deterministic_regardless_of_key_order():
    payload_a = {"amount": 100, "txid": "abc123"}
    payload_b = {"txid": "abc123", "amount": 100}
    assert sign_payload(payload_a, "secret") == sign_payload(payload_b, "secret")


def test_verify_accepts_valid_signature():
    payload = {"amount": 100, "txid": "abc123"}
    sig = sign_payload(payload, "secret")
    assert verify_signature(payload, "secret", sig) is True


def test_verify_rejects_tampered_payload():
    payload = {"amount": 100, "txid": "abc123"}
    sig = sign_payload(payload, "secret")
    tampered = {"amount": 999, "txid": "abc123"}
    assert verify_signature(tampered, "secret", sig) is False


def test_verify_rejects_wrong_secret():
    payload = {"amount": 100, "txid": "abc123"}
    sig = sign_payload(payload, "secret")
    assert verify_signature(payload, "other-secret", sig) is False
