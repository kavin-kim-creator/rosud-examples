/**
 * TypeScript + Rosud — Payment between AI agents
 */
import Rosud from 'rosud';

const client = new Rosud({ apiKey: process.env.ROSUD_API_KEY! });

async function main() {
  // Check balance
  const balance = await client.wallets.balance();
  console.log(`Balance: ${balance.usdc} USDC`);

  // Send payment
  const payment = await client.payments.create({
    amount: 0.10,
    to: '0x742d35Cc6634C0532925a3b8D4C9E3Ff9C4A6bB',
    memo: 'inference_fee',
  });
  console.log(`Payment: ${payment.status} | ${payment.txHash}`);
}

main().catch(console.error);
