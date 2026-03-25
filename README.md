# rosud-examples

> Real-world examples for [Rosud](https://rosud.com) — USDC payment infrastructure for AI agents.

```bash
pip install rosud
```

## Examples

| Example | Framework | Description |
|---------|-----------|-------------|
| [basic/](basic/) | Pure Python | Simple payment, balance check |
| [crewai/](crewai/) | CrewAI | Multi-agent task with payments |
| [openai-agents/](openai-agents/) | OpenAI Agents SDK | Tool-calling payment agent |
| [mcp/](mcp/) | MCP Server | Claude desktop integration |
| [typescript/](typescript/) | TypeScript SDK | Node.js payment flow |
| [webhooks/](webhooks/) | FastAPI | Real-time payment event handling |

## Quick Start

```python
import rosud

client = rosud.Rosud(api_key="rosud_live_xxx")

# Agent pays for API call
payment = client.payments.create(
    amount=0.01,
    to="0xRecipientAddress",
    memo="gpt4_inference_fee"
)
print(payment.status)  # "confirmed"
```

## Why Rosud?

AI agents need to **pay each other autonomously** — without human approval, without credit cards, without gas fee complexity.

Rosud provides:
- ✅ USDC on Base L2 (fast, cheap)
- ✅ Spend limits (agents can't go rogue)
- ✅ MCP native (Claude integration in 1 line)
- ✅ Webhook notifications
- ✅ No crypto complexity for developers

## Docs

→ [rosud.com/docs](https://rosud.com/docs)
