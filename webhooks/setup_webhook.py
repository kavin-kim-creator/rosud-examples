"""
Webhook Registration Script

Registers a webhook endpoint with Rosud once.

Usage:
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
        # Check for existing webhooks (prevent duplicates)
        existing = client.webhooks.list()
        for wh in existing:
            if wh.url == webhook_url:
                print(f"⚠️  Webhook already registered: {wh.id}")
                print(f"   URL: {wh.url}")
                client.close()
                return

        # Register new webhook
        webhook = client.webhooks.create(
            url=webhook_url,
            events=["payment.confirmed", "payment.failed", "payment.pending"],
            secret=webhook_secret,
        )

        print(f"✅ Webhook registered!")
        print(f"   ID: {webhook.id}")
        print(f"   URL: {webhook.url}")
        print(f"   Events: {', '.join(webhook.events)}")
        print()
        print("💡 Now run the receive.py server:")
        print("   uvicorn receive:app --host 0.0.0.0 --port 8000")

    except RosudError as e:
        print(f"❌ Webhook registration failed: {e.message}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
