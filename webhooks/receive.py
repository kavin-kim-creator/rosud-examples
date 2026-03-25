"""
Rosud Webhook Handler — FastAPI 예시

Rosud 결제 이벤트를 실시간으로 수신하는 웹훅 서버.

설치:
    pip install rosud fastapi uvicorn

실행:
    export ROSUD_API_KEY=rosud_live_xxx
    export ROSUD_WEBHOOK_SECRET=your-secret-key
    uvicorn receive.py:app --host 0.0.0.0 --port 8000

웹훅 등록 (한 번만):
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
# 서명 검증
# ──────────────────────────────────────────────────────────

def verify_signature(body: bytes, signature_header: str, secret: str) -> bool:
    """
    Rosud 웹훅 HMAC-SHA256 서명 검증.
    서명 형식: "t=<timestamp>,v1=<hex-signature>"
    """
    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        timestamp = int(parts["t"])
        received_sig = parts["v1"]
    except (ValueError, KeyError):
        return False

    # 5분 타임스탬프 윈도우 (replay attack 방어)
    if abs(int(time.time()) - timestamp) > 300:
        return False

    # HMAC 계산
    signed = f"{timestamp}.{body.decode('utf-8')}".encode()
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_sig)


# ──────────────────────────────────────────────────────────
# 웹훅 엔드포인트
# ──────────────────────────────────────────────────────────

@app.post("/webhooks/rosud")
async def receive_rosud_event(
    request: Request,
    x_rosud_signature: str = Header(..., alias="X-Rosud-Signature"),
) -> dict:
    """
    Rosud 결제 이벤트 수신.

    이벤트 타입:
      - payment.confirmed  → 결제 완료 (on-chain confirmed)
      - payment.failed     → 결제 실패
      - payment.pending    → 결제 처리 중
    """
    body = await request.body()

    # 1. 서명 검증 (보안 필수!)
    if not verify_signature(body, x_rosud_signature, ROSUD_WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # 2. 이벤트 파싱
    event = json.loads(body)
    event_type = event.get("type")
    data = event.get("data", {})

    print(f"📨 Rosud 이벤트 수신: {event_type}")

    # 3. 이벤트 타입별 처리
    if event_type == "payment.confirmed":
        payment_id = data.get("id")
        amount = data.get("amount")
        currency = data.get("currency", "USDC")
        memo = data.get("memo", "")
        tx_hash = data.get("tx_hash")

        print(f"  ✅ 결제 완료: {payment_id}")
        print(f"     금액: {amount} {currency}")
        print(f"     메모: {memo}")
        print(f"     TX: {tx_hash}")

        # 여기에 비즈니스 로직 추가:
        # - DB 결제 상태 업데이트
        # - 서비스 제공 트리거
        # - 영수증 이메일 발송

    elif event_type == "payment.failed":
        payment_id = data.get("id")
        error_reason = data.get("error", "unknown")

        print(f"  ❌ 결제 실패: {payment_id} — {error_reason}")

        # 여기에 실패 처리:
        # - 사용자 알림
        # - 재시도 큐에 추가

    elif event_type == "payment.pending":
        payment_id = data.get("id")
        print(f"  ⏳ 결제 대기: {payment_id}")

    else:
        print(f"  ⚠️  알 수 없는 이벤트: {event_type}")

    # Rosud에게 즉시 200 응답 (타임아웃 방지)
    return {"ok": True, "received": event_type}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "rosud-webhook-handler"}
