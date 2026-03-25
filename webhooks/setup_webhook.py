"""
웹훅 등록 스크립트

Rosud에 웹훅 엔드포인트를 한 번 등록합니다.

사용법:
    export ROSUD_API_KEY=rosud_live_xxx
    export ROSUD_WEBHOOK_SECRET=your-secret-key
    export WEBHOOK_URL=https://myapp.com/webhooks/rosud
    python setup_webhook.py
"""
import os
import rosud
from rosud.exceptions import RosudError

def main() -> None:
    client = rosud.Rosud(api_key=os.environ.get("ROSUD_API_KEY", "rosud_live_xxx"))

    webhook_url = os.environ.get("WEBHOOK_URL", "https://myapp.com/webhooks/rosud")
    webhook_secret = os.environ.get("ROSUD_WEBHOOK_SECRET", "change-me-in-production")

    try:
        # 기존 웹훅 확인 (중복 방지)
        existing = client.webhooks.list()
        for wh in existing:
            if wh.url == webhook_url:
                print(f"⚠️  이미 등록된 웹훅: {wh.id}")
                print(f"   URL: {wh.url}")
                client.close()
                return

        # 웹훅 신규 등록
        webhook = client.webhooks.create(
            url=webhook_url,
            events=["payment.confirmed", "payment.failed", "payment.pending"],
            secret=webhook_secret,
        )

        print(f"✅ 웹훅 등록 완료!")
        print(f"   ID: {webhook.id}")
        print(f"   URL: {webhook.url}")
        print(f"   이벤트: {', '.join(webhook.events)}")
        print()
        print("💡 이제 receive.py 서버를 실행하세요:")
        print("   uvicorn receive:app --host 0.0.0.0 --port 8000")

    except RosudError as e:
        print(f"❌ 웹훅 등록 실패: {e.message}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
