"""
CrewAI + Rosud — Agents that pay each other for specialized tasks.

Use case: Research agent hires Analyst agent, pays per report.
"""
from crewai import Agent, Task, Crew
from crewai.tools import tool
import rosud

rosud_client = rosud.Rosud(api_key="rosud_live_xxx")

ANALYST_WALLET = "0xAnalystAgentWalletAddress"
RATE_PER_REPORT = 0.50  # 0.50 USDC per analysis

@tool("pay_for_analysis")
def pay_for_analysis(task_description: str) -> str:
    """Pay the analyst agent 0.50 USDC for completing a research task."""
    payment = rosud_client.payments.create(
        amount=RATE_PER_REPORT,
        to=ANALYST_WALLET,
        memo=f"analysis: {task_description[:50]}"
    )
    return f"Payment sent: {payment.status} (tx: {payment.tx_hash})"

@tool("check_budget")
def check_budget() -> str:
    """Check remaining USDC budget before commissioning tasks."""
    balance = rosud_client.wallets.balance()
    return f"Available: {balance.usdc} USDC"

# Research agent that commissions work and pays
researcher = Agent(
    role="Research Coordinator",
    goal="Gather market intelligence by hiring specialist agents",
    tools=[check_budget, pay_for_analysis],
    verbose=True
)

# Analyst agent that does the work
analyst = Agent(
    role="Market Analyst",
    goal="Provide detailed analysis reports on AI infrastructure market",
    verbose=True
)

task1 = Task(
    description="Check budget, then commission market analysis on AI payment infrastructure. Pay after receiving the report.",
    agent=researcher
)

task2 = Task(
    description="Analyze the AI agent payment infrastructure market. Compare Rosud, Skyfire, and Coinbase x402. Provide a 200-word summary.",
    agent=analyst
)

crew = Crew(agents=[researcher, analyst], tasks=[task1, task2])
result = crew.kickoff()
print(result)
