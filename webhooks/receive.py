"""
Rosud Webhook Handler — FastAPI example

Webhook server for receiving Rosud payment events in real time.

Setup:
    pip install rosud fastapi uvicorn

Run:
    export ROSUD_API_KEY=rosud_live_xxx
    export ROSUD_WEBHOOK_SECRET=your-secret-key
    uvicorn receive.py:app --host 0.0.0.0 --port 8000

Register webhook (once only):
    python setup_webhook.py
"""
import hashlib
import hmac
import json
import os
import time

import rosud
from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI(title="Rosud Webhook Server")

ROSUD_WEBHOOK_SECRET = os.environ.get("ROSUD_WEBHOOK_SECRET", "change-me-in-production")


# ──────────────────────────────────────────────────────────
# Signature verification
# ──────────────────────────────────────────────────────────

def verify_signature(body: bytes, signature_header: str, secret: str) -> bool:
    """
    Rosud webhook HMAC-SHA256 signature verification.
    Signature format: "t=<timestamp>,v1=<hex-signature>"
    """
    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        timestamp = int(parts["t"])
        received_sig = parts["v1"]
    except (ValueError, KeyError):
        return False

    # 5-minute timestamp window (replay attack protection)
    if abs(int(time.time()) - timestamp) > 300:
        return False

    # Calculate HMAC
    signed = f"{timestamp}.{body.decode('utf-8')}".encode()
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_sig)


# ──────────────────────────────────────────────────────────
# Webhook endpoint
# ──────────────────────────────────────────────────────────

@app.post("/webhooks/rosud")
async def receive_rosud_event(
    request: Request,
    x_rosud_signature: str = Header(..., alias="X-Rosud-Signature"),
) -> dict:
    """
    Receive Rosud payment events.

    Event types:
      - payment.confirmed  → Payment complete (on-chain confirmed)
      - payment.failed     → Payment failed
      - payment.pending    → Payment processing
    """
    body = await request.body()

    # 1. Verify signature (required for security!)
    if not verify_signature(body, x_rosud_signature, ROSUD_WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. Parse event
    event = json.loads(body)
    event_type = event.get("type")
    data = event.get("data", {})

    print(f"📨 Rosud event received: {event_type}")

    # 3. Handle by event type
    if event_type == "payment.confirmed":
        payment_id = data.get("id")
        amount = data.get("amount")
        currency = data.get("currency", "USDC")
        memo = data.get("memo", "")
        tx_hash = data.get("tx_hash")

        print(f"  ✅ Payment confirmed: {payment_id}")
        print(f"     Amount: {amount} {currency}")
        print(f"     Memo: {memo}")
        print(f"     TX: {tx_hash}")

        # Add your business logic here:
        # - Update DB payment status
        # - Trigger service delivery
        # - Send receipt email

    elif event_type == "payment.failed":
        payment_id = data.get("id")
        error_reason = data.get("error", "unknown")

        print(f"  ❌ Payment failed: {payment_id} — {error_reason}")

        # Handle failure here:
        # - Notify user
        # - Add to retry queue

    elif event_type == "payment.pending":
        payment_id = data.get("id")
        print(f"  ⏳ Payment pending: {payment_id}")

    else:
        print(f"  ⚠️  Unknown event: {event_type}")

    # Return 200 immediately to Rosud (prevent timeout)
    return {"ok": True, "received": event_type}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "rosud-webhook-handler"}
