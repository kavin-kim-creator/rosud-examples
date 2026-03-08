"""
OpenAI Agents SDK + Rosud — Tool-calling agent that manages payments.
"""
from agents import Agent, Runner, function_tool
import rosud

client = rosud.Rosud(api_key="rosud_live_xxx")

@function_tool
def send_payment(amount: float, to_address: str, memo: str) -> dict:
    """Send USDC payment to another agent or service."""
    payment = client.payments.create(amount=amount, to=to_address, memo=memo)
    return {"status": payment.status, "tx_hash": payment.tx_hash, "amount": amount}

@function_tool
def get_balance() -> dict:
    """Get current USDC wallet balance."""
    balance = client.wallets.balance()
    return {"usdc": balance.usdc, "wallet": balance.address}

payment_agent = Agent(
    name="PaymentAgent",
    instructions="""You are an AI agent with a USDC wallet on Base L2.
    You can send payments to other agents for services rendered.
    Always check balance before sending. Never exceed 1 USDC per transaction without explicit approval.""",
    tools=[send_payment, get_balance],
)

result = Runner.run_sync(
    payment_agent,
    "Check my balance and send 0.05 USDC to 0x742d35Cc6634C0532925a3b8D4C9E3Ff9C4A6bB for the completed research task."
)
print(result.final_output)
