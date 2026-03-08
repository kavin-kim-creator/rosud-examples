"""
Basic Rosud example — single payment between agents.
"""
import rosud

client = rosud.Rosud(api_key="rosud_live_xxx")
# or: export ROSUD_API_KEY=rosud_live_xxx

# 1. Check balance
balance = client.wallets.balance()
print(f"Balance: {balance.usdc} USDC")

# 2. Send payment
payment = client.payments.create(
    amount=0.10,
    to="0x742d35Cc6634C0532925a3b8D4C9E3Ff9C4A6bB",
    memo="research_task_fee"
)
print(f"Payment: {payment.status} | tx: {payment.tx_hash}")

# 3. Verify
result = client.payments.get(payment.id)
print(f"Confirmed: {result.confirmed_at}")
