---
name: perp-trading-automation
description: >
  Build and operate non-custodial automated trading bots for decentralized
  perpetual exchanges (Hyperliquid, Aster DEX, GMX) on EVM chains
  (Arbitrum, Base). Handles RPC connectivity, wallet management, position
  lifecycle, funding rate monitoring, risk controls, and circuit breakers.
  Includes full Hyperliquid order execution implementation.
trigger_keywords:
  - perp trading
  - perpetual exchange
  - trading bot
  - hyperliquid
  - aster dex
  - gmx
  - decentralized trading
  - crypto bot
  - funding rate
  - dex client
  - risk engine
  - circuit breaker
---

# Perp Trading Automation Skill

## Overview

Production-grade toolkit for building non-custodial automated trading
infrastructure for decentralized perpetual exchanges.

**Implemented:**
- **Hyperliquid** — Full order lifecycle (place, cancel, close, funding rates, positions, leverage)
| 4.0.0 | 2026-06-01 | Aster DEX full client: `fapi.asterdex.com` REST API, HMAC SHA256 auth, 602 markets, order placement, account mgmt, normalized funding rates; multi-exchange TradingBot; hourly cron; pitfalls: suffix stripping, batch ticker, base URL; ref `references/aster-dex-api-reference.md` |
- **Hyperliquid Risk Engine** — 10-layer risk validation + circuit breakers
- **Trading Bot Orchestrator** — Strategy plugin interface, main loop, graceful shutdown, multi-exchange support (Hyperliquid + Aster)
- **EVM Chain Client** — ETH/ERC-20 balance reads on Arbitrum, Base, Ethereum, Avalanche

**NOT Implemented (by design — requires strategy decisions):**
- Signal generation (strategy engine interface provided)
- Leverage optimization
- Cross-exchange arbitrage

---

## Project Structure

```
perp-trading-bot/
├── src/
│   ├── dex_client.py            # Chain RPC client
│   ├── hyperliquid_client.py    # Full Hyperliquid API client
│   ├── aster_client.py          # Aster DEX Futures API client (v2, 602 markets)
│   ├── risk_engine.py           # Risk management engine
│   └── trading_bot.py           # Main orchestrator (multi-exchange)
├── config/.env.example          # Config template
├── testnet_logs/                # Execution traces
└── RUNBOOK.md                   # Operational runbook
```

---

## Quick Start

```bash
cd /data/workspace/perp-trading-bot
source .venv/bin/activate

# Install deps
pip install web3==7.16.0 eth-account==0.13.7 requests==2.34.2

# Validate (no orders)
python3 src/dex_client.py
python3 src/trading_bot.py --dry-run
```

---

## HyperliquidClient API

### Initialization

```python
from src.hyperliquid_client import HyperliquidClient

# Reads HYPERLIQUID_API_WALLET_KEY and HYPERLIQUID_MAIN_WALLET from env
client = HyperliquidClient()

# Or pass explicitly
client = HyperliquidClient(
    api_wallet_private_key="0x...",
    main_wallet_address="0xYourMainWallet...",
    is_testnet=False,
)
```

### Public Reads (No API Key)

```python
# Funding rates (all markets, 230+ assets)
rates = HyperliquidClient.get_funding_rates_static()
# [{"coin": "BTC", "funding_rate": "0.0000125", "mark_price": "73604.0"}, ...]

# Meta + asset contexts
meta = client.get_meta()
orderbook = client.get_orderbook("BTC", depth=20)
```

### Account Management

```python
# Account summary (margin, positions, withdrawable)
summary = client.get_account_summary()
# {"account_value": "10000.0", "withdrawable": "5000.0", ...}

# Open positions
positions = client.get_open_positions()
# [{"coin": "BTC", "size": "0.01", "entry_price": "73000", ...}]

# Update leverage
client.update_leverage("BTC", leverage=3, cross=True)
```

### Order Placement

```python
# Place limit order
result = client.place_order(
    coin="BTC",
    is_buy=True,
    size="0.01",
    limit_price="73500.0",
    reduce_only=False,
    order_type="limit",
    time_in_force="Gtc",   # Gtc, Ioc, Alo
)

# Cancel order
client.cancel_order("BTC", oid=12345)

# Open/close position (convenience wrappers)
client.open_position("BTC", "long", Decimal("0.01"), leverage=3)
client.close_position("BTC")
```

### Error Handling

| Error | Meaning | Fix |
|---|---|---|
| `User or API Wallet 0x0 does not exist` | API wallet not approved | Use `Approve API Wallet` HL action first |
| `Insufficient margin` | Not enough funds | Deposit USDC to Hyperliquid |
| `Order rejected` | Price/size outside limits | Check tick size, lot size |

---

## AsterClient API

### Initialization

```python
from src.aster_client import AsterClient

# Public data only (no API key needed)
client = AsterClient()

# With API key for trading
client = AsterClient(
    api_key="your-api-key",
    api_secret="your-api-secret",
)
# Or set ASTER_API_KEY and ASTER_API_SECRET env vars
```

### Public Market Data (No Auth)

```python
# Funding rates (all 602 markets)
rates = client.get_funding_rates()
# [{"symbol": "BTCUSDT", "funding_rate": "0.0001", "mark_price": "71790.3", ...}]

# Normalized format (compatible with HyperliquidClient / strategy code)
rates = client.get_funding_rates_normalized()
# [{"coin": "BTC", "symbol": "BTCUSDT", "funding_rate": "0.0001", ...}]

# Static method (no instantiation needed)
rates = AsterClient.get_funding_rates_static()

# Orderbook
ob = client.get_orderbook("BTCUSDT", limit=20)
# {"bids": [[price, qty], ...], "asks": [[price, qty], ...]}

# Mark price + funding rate
mp = client.get_mark_price("BTCUSDT")
# {"mark_price": Decimal("71790.3"), "funding_rate": "0.0001", ...}

# 24hr ticker
ticker = client.get_24hr_ticker("BTCUSDT")

# Klines/candles
klines = client.get_klines("BTCUSDT", interval="1h", limit=100)

# All trading symbols
symbols = client.get_symbols()
```

### Authenticated Endpoints (API Key + Secret Required)

```python
# Account balance
balances = client.get_account_balance()

# Account info + positions
account = client.get_account_info()

# Open positions
positions = client.get_open_positions()
# [{"symbol": "BTCUSDT", "coin": "BTC", "size": "0.01", "entry_price": "71000", ...}]

# Place orders
result = client.place_market_order("BTCUSDT", "BUY", "0.01")
result = client.place_limit_order("BTCUSDT", "SELL", "0.01", "75000", "GTC")
result = client.place_order(
    symbol="BTCUSDT", side="BUY", quantity="0.01",
    price="71000", order_type="LIMIT", time_in_force="GTC",
    leverage=3, reduce_only=False,
)

# Cancel orders
client.cancel_order("BTCUSDT", order_id=12345)
client.cancel_all_orders("BTCUSDT")

# Change leverage
client.change_leverage("BTCUSDT", 5)

# Convenience wrappers
client.open_position("BTCUSDT", "long", Decimal("100"), leverage=3)
client.close_position("BTCUSDT")

# Income history (funding fees, commissions, PNL)
income = client.get_income_history(symbol="BTCUSDT", income_type="FUNDING_FEE")
```

### Key Differences from HyperliquidClient

| Feature | HyperliquidClient | AsterClient |
|---|---|---|
| Auth | API wallet private key (EIP-712) | API key + HMAC SHA256 |
| Order signing | L1 action hash | REST params + signature |
| Symbol format | "BTC" | "BTCUSDT" |
| Base URL | `api.hyperliquid.xyz` | `fapi.asterdex.com` |
| Markets | 230+ crypto | 602 (crypto + stocks + commodities) |
| Rate limit | Not documented | 2400 req/min, 1200 orders/min |

### Important Notes

1. Aster uses **HMAC SHA256** signing (not EIP-712 like Hyperliquid)
2. Symbol format is **"BTCUSDT"** (not "BTC") — use `get_funding_rates_normalized()` for compatible format
3. Base URL is **`https://fapi.asterdex.com`** (NOT `https://api.asterdex.com`)
4. Aster has **602 markets** including stock perps (TSLA, AMZN, AAPL, etc.)
5. The `get_funding_rates_normalized()` method strips "USDT"/"USD" suffixes and maps to the format expected by `SmartFundingStrategy`

## Aster DEX API Reference

- `references/aster-dex-api-reference.md` — Full endpoint docs, auth details, symbol formats, rate limits, response schemas, error codes

---

## RiskEngine API

```python
from src.risk_engine import RiskEngine, RiskLimits, PositionState
from decimal import Decimal

engine = RiskEngine(limits=RiskLimits(
    max_position_size_usd=Decimal("1000"),
    max_leverage=5,
    max_daily_loss_usd=Decimal("100"),
))

# Pre-trade validation
is_valid, reason = engine.validate_new_position(
    coin="BTC", side="long",
    size_usd=Decimal("500"),
    leverage=3,
    current_price=Decimal("73500"),
    funding_rate=Decimal("0.00001"),
)

# Track positions
engine.register_position(PositionState(
    coin="BTC", side="long",
    size_usd=Decimal("500"),
    leverage=3,
    entry_price=Decimal("73500"),
))

# Update P&L
engine.update_position_pnl("BTC", Decimal("74000"))

# Check status
status = engine.get_status_report()
# {"trading_halted": false, "open_positions": 1, ...}

# Circuit breaker
warnings = engine.check_liquidation_warnings({"BTC": Decimal("72000")})
# Returns liquidation warnings

# Emergency
engine._trigger_halt("Manual halt")
engine.manual_resume()
```

---

## TradingBot Orchestrator

```python
from src.trading_bot import TradingBot, StrategyEngine

# Custom strategy
class FundingRateStrategy(StrategyEngine):
    def generate_signals(self, market_data: dict) -> list[dict]:
        signals = []
        for coin, rate in market_data["funding_rates"].items():
            if float(rate) < -0.0001:
                signals.append({
                    "coin": coin, "side": "long",
                    "size_usd": 100, "leverage": 2,
                    "reason": "negative_funding",
                })
        return signals

# Run
bot = TradingBot(
    strategy=FundingRateStrategy(),
    exchange="hyperliquid",
    dry_run=True,        # Always start with dry_run!
    poll_interval=60,
)
bot.run()  # Main loop with graceful shutdown
```

**CLI:**
```bash
python3 src/trading_bot.py --dry-run --interval 30
python3 src/trading_bot.py --live --exchange hyperliquid
```

---

## Security Checklist

- [ ] Dedicated trading wallet (NOT main wallet)
- [ ] `.env` has `chmod 600`
- [ ] API wallet approved on Hyperliquid
- [ ] Risk limits configured conservatively
- [ ] Tested on dry-run for 24h before live
- [ ] Emergency stop tested

---

## Self-Improvement Directive

The user has explicitly asked the agent to **continuously self-improve the trading bot** without waiting for instructions. After each session or when idle:

1. Review the latest bot performance (check `testnet_logs/paper_status.json`, `testnet_logs/paper_trades.json`)
2. Identify underperforming positions, false signals, or missed opportunities
3. Propose and implement improvements to strategy, risk limits, or filters
4. Restart the bot with improved config
5. Document changes in the version history table and pitfalls

**Standing constraints:**
- Capital: $100 (never change without explicit user approval)
- Paper trading only (no live trades without explicit user authorization)
- All changes must be tested (syntax check + brief dry-run) before restarting the bot
- Document every change in the SKILL.md version table

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2025-05-31 | Initial: dex_client.py, Hyperliquid reads, ERC-20, position stubs |
| 2.0.0 | 2025-05-31 | Full Hyperliquid order execution, risk engine, trading bot orchestrator, Aster stub, runbook |
| 3.0.0 | 2026-06-01 | Paper trading simulator, FundingRateStrategy, background bot launch, monitoring cron pattern, hyperliquid volume field fix (`dayNtlVlm`), risk engine seeding for paper mode |
| 3.2.0 | 2026-06-01 | Claude Code delegation: auth cross-user setup, print-mode API key requirement vs OAuth interactive, approval mode config; new ref `claude-code-auth-and-delegation.md` |
| 4.1.0 | 2026-06-01 | Claude Code delegation: SDK+OAuth approach (no API key needed), wrapper script, Docker tmux pitfall, unset ANTHROPIC_API_KEY gotcha |
| 4.2.0 | 2026-06-01 | Strategy v2.1 tuning: entry threshold 0.005%→0.003%, min volume $5M→$2M, stop loss 3%→4%, EMA20 trend filter relaxed to >2% deviation; v2.0 was too idle (only 2 markets passed filters in 3h) |

## Paper Trading (NEW — v3.0)

### Starting Paper Trading

```bash
cd /data/workspace/perp-trading-bot
source .venv/bin/activate

# 48-hour paper trading run (default $10k capital, 60s poll interval)
python3 src/paper_trading_bot.py \
    --capital 10000 \
    --interval 60 \
    --duration 172800 \
    --entry-threshold 0.00003 \
    --max-position 300
```

### Background Launch Pattern

For long-running bounded tasks, use `terminal(background=true)`:

```python
terminal(
    command="cd /path && source .venv/bin/activate && exec python3 script.py --duration 172800",
    background=true,
)
# Then poll with: process(action='poll', session_id=...)
# Check log file directly: terminal(command="tail -f /path/log.log")
```

**Important:** Do NOT use `terminal(background=true)` without `notify_on_complete=true` for bounded tasks unless you have an external monitoring mechanism (cron, log tailing). The hint warning about silent background processes is real — if nothing monitors the log, you will never know when it finishes.

### Monitoring Pattern

For 48h+ runs, combine:
1. **Cron job** (`cronjob(action='create', schedule='0 */6 * * *')`) — periodic status reports delivered to `origin`
2. **JSON status file** — bot writes `testnet_logs/paper_status.json` each cycle
3. **Trade log** — bot writes `testnet_logs/paper_trades.json` on shutdown
4. **Final report** — `testnet_logs/paper_final_report.json` on shutdown
5. **pgrep check** — `pgrep -f paper_trading_bot.py` for liveness

### Strategy: Funding Rate Mean-Reversion

Implemented in `src/paper_trading_bot.py` as `FundingRateStrategy` class:
- Entry when |funding_rate| > entry_threshold AND 24h volume > $1M
- Exit when: funding reverts, take-profit hit, or stop-loss hit
- Only trade markets with >$1M daily volume (avoids memecoin slippage)
- Max 3 concurrent positions, max $300 each during paper testing

### Known Pitfalls (v3.0)

1. **Hyperliquid API field is `dayNtlVlm` NOT `day_volume`** — Always use `rate.get('day_volume', rate.get('dayNtlVlm', 0))` in strategies that filter by volume. The wrong name silently returns 0 for all markets.

2. **`get_funding_rates_static()` must include volume fields** — If strategy depends on `dayNtlVlm` or `openInterest`, add them to the static method's response dict.

3. **Risk engine must be seeded for paper mode** — `RiskEngine.validate_new_position` checks `required_margin > available_margin`. Without seeding account_value/withdrawable, all paper trades are rejected. Fix: call `risk.update_account_value(capital, capital)` at init.

4. **Funding rates change every cycle** — The strategy re-fetches live data each poll interval, so signals are always current. No caching needed, but be mindful of the 1200 req/min rate limit if interval < 1s.

5. **`self._duration` rename trap** — If renaming `self.duration_seconds`, grep ALL references before the rename to avoid `AttributeError` at runtime.

### Strategy: Smart Funding Arbitrage v2 (NEW — v3.1)

Rewritten as `SmartFundingStrategy` in `src/paper_trading_bot.py`. Key improvements over v1:

**Filters (all must pass to open):**
1. **EMA20 trend filter** — Only long if price > EMA20, only short if below. Prevents catching falling knives.
2. **Bid-ask spread filter** — Skip markets with spread > 0.5%. Avoids thin order books that eat profits.
3. **Funding rate history** — Compare current rate to 8-sample rolling average. Only trade if current is 2x the average (spike, not drift).
4. **Volume filter** — $5M minimum 24h volume (up from $1M in v1).
5. **Entry threshold** — 0.005% (5 bps), up from 0.001% in v1. Only extreme funding.

**Position Management:**
- **Size**: $10-15 max (10-15% of $100 capital), down from $300 in v1
- **Max positions**: 2 (concentrated, not diluted), down from 3
- **Stop loss**: 3% (wider to avoid noise at 3x leverage), up from 1%
- **Take profit**: 3%, up from 2%
- **Funding-flip exit**: Close immediately if funding sign flips against position

**Config for $100 capital:**
```python
RiskLimits(
    max_position_size_usd=Decimal("20"),
    max_leverage=3,
    max_daily_loss_usd=Decimal("10"),
    max_total_exposure_usd=Decimal("40"),
    max_concurrent_positions=2,
    circuit_breaker_drawdown_pct=Decimal("15"),
)
```

### Known Pitfalls (v3.1)

6. **PriceRateHistory type hint** — In `generate_signals()` signature, use `PriceHistory` not `PriceRateHistory`. The class is named `PriceHistory`; `PriceRateHistory` causes `NameError` at class definition time.

### Claude Code CLI Delegation (for coding-heavy tasks)

**Recommended approach: Use `claude-agent-sdk` (Python) with OAuth.**

The `claude-agent-sdk` v0.2.87 is pre-installed at `/usr/local/lib/python3.13/site-packages`. It provides `ClaudeSDKClient` for programmatic delegation and works with OAuth credentials (no API key needed).

**Critical:** `ANTHROPIC_API_KEY` must be **unset** before using the SDK with OAuth. If it's set to the OAuth access token (which happens after `claude auth login`), the SDK gets HTTP 401.

```python
import os
env = os.environ.copy()
env.pop("ANTHROPIC_API_KEY", None)  # Must unset for OAuth to work
os.environ.update(env)

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

async def delegate(task, cwd="/data/workspace/perp-trading-bot"):
    options = ClaudeAgentOptions(
        model="sonnet",
        permission_mode="bypassPermissions",
        cwd=cwd,
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query(task)
        async for msg in client.receive_response():
            ...
```

**Wrapper script:** `/data/workspace/perp-trading-bot/scripts/claude_delegate.py` handles env cleanup automatically:
```bash
python3 scripts/claude_delegate.py "Your task here"
```

**User preference on delegation:** All logic-heavy coding tasks (strategy changes, new features, refactoring, bug analysis) MUST be delegated to Claude Code via the SDK wrapper. The agent should only do simple one-liner edits directly. Always use `model="sonnet"` and `permission_mode="bypassPermissions"`.

**Auth setup for non-root users:** Copy credentials from root:
```bash
mkdir -p /data/.claude
cp /root/.claude/.credentials.json /data/.claude/.credentials.json
chown -R hermes:hermes /data/.claude/
```

**Do NOT use tmux for Claude Code in Docker** — the tmux server won't persist. Use the SDK approach instead.

## Delegation Reference

- `references/claude-code-auth-and-delegation.md` — Claude Code CLI auth across users, print-mode vs interactive-mode requirements, approval config

7. **Slippage realism for micro positions** — At $10-15 position sizes on altcoins, even 0.05% slippage can be proportionally large. Consider 0.1% for liquid markets on Hyperliquid, or model explicit bid-ask spread per market.

8. **EMA20 warmup period** — PriceHistory needs 20 samples before EMA is calculated. During warmup, `is_above_ema()` returns `None` and the trend filter passes (no filter). This is intentional — no data means no filter. After ~10 minutes at 30s intervals, EMA activates.

9. **Funding rate history window** — 8 samples at 30s intervals = 4 minutes of history. This is intentionally short for responsiveness. At longer intervals (60s+), increase the window proportionally.

### Known Pitfalls (v4.0)

10. **Aster symbol suffix stripping — use `endswith()` not `replace()`** — `symbol.replace("USDT", "").replace("USD", "")` looks correct but `replace()` replaces ALL occurrences mid-string. A symbol like `USDTUSDT` would become empty. Always use the `endswith()` + slice pattern from `get_funding_rates_normalized()`.

11. **Aster per-symbol ticker endpoint is unreliable** — `GET /fapi/v1/ticker/24hr?symbol=GNSUSD` returns HTTP 400 for some symbols. Always use the batch endpoint (no symbol param) and build a local map, rather than querying per-symbol in a loop. The `get_funding_rates_normalized()` method already does this correctly.

12. **Aster base URL is `fapi.asterdex.com` not `api.asterdex.com`** — The old stub had the wrong base URL. All Futures REST calls go to `https://fapi.asterdex.com`. WebSocket streams go to `wss://fstream.asterdex.com`.

13. **Strategy v2.0 was too conservative for live market conditions** — With 0.005% entry threshold + $5M min volume + strict EMA20 trend filter, only 2-3 markets passed all filters at any time. The bot sat idle for hours. Tuned in v2.1: 0.003% threshold, $2M volume, relaxed EMA20 (>2% deviation only). Result: bot opens positions within first cycle.

14. **Stop loss too tight for volatile alts** — PUMP (micro-cap alt) was stopped out at 3% despite having strong negative funding. Either widen to 4% (v2.1) or add a market-cap/volatility filter to avoid the most volatile micro-caps entirely.

15. **Strict EMA20 trend filter blocks valid funding signals** — Requiring price > EMA20 for longs blocked entries on assets with strong negative funding that were slightly below their EMA. The relaxed filter (>2% deviation threshold) lets through mild counter-trend entries while still avoiding catching falling knives in strong downtrends.

## Pitfalls Reference

- `references/session-research-and-pitfalls.md` — original research, Hyperliquid API quirks, container pitfalls
- `references/paper-trading-research-and-pitfalls.md` — paper trading-specific pitfalls, strategy traps, monitoring patterns
