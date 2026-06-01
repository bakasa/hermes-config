# Paper Trading Bot — Research & Pitfalls Reference

## Session: 2026-06-01 (Phase 5 — Paper Trading Strategy & Sandbox)

### Strategy Implementation: Funding Rate Mean-Reversion

**Signal Logic:**
- Funding rate < -entry_threshold → open_long (receive funding payments)
- Funding rate > +entry_threshold → open_short (receive funding payments)
- Exit when: funding reverts (|rate| < exit_threshold) OR take-profit hit OR stop-loss hit

**Strategy Parameters (defaults tested):**
- `entry_threshold = 0.00003` (0.003%)
- `exit_threshold = 0.00001` (0.001%)
- `take_profit_pct = 2.0%`
- `stop_loss_pct = 1.0%`
- `max_position_usd = 300`
- `max_positions = 3`
- `min_24h_volume_usd = 1_000_000`

### Pitfalls Encountered & Fixes

1. **`day_volume` field name was WRONG in strategy**
   - Hyperliquid API returns `dayNtlVlm` not `day_volume`
   - Fix: `rate.get('day_volume', rate.get('dayNtlVlm', 0))`
   - Impact: ALL markets appeared to have 0 volume → volume filter silently blocked every signal → 0 trades for minutes

2. **`get_funding_rates_static()` didn't include volume or OI fields**
   - Original implementation only returned `coin`, `funding_rate`, `mark_price`
   - Fix: added `dayNtlVlm` and `open_interest` to the response dict

3. **Risk engine rejected all paper trades because `account_value = 0`**
   - `validate_new_position` checks `required_margin > available_margin`; available = withdrawable - margin_used; with account_value=0, available=-100 → all rejected
   - Fix: seed `self.risk.update_account_value(initial_capital, initial_capital)` at bot init

4. **Funding rate API results include memecoins; volume/$ filters are essential**
   - Top funding rates were ZORA, AZTEC, ALT (memecoins with <$1M volume)
   - Without volume filter, strategy would trade illiquid markets with wide spreads
   - With $1M volume filter, only 6/230 markets qualified on first run

5. **Paper trading P&L has slippage cost**
   - Default 0.05% slippage on each fill means round-trip cost is 0.1% + funding
   - Strategy must overcome this cost to be profitable

6. **`self.duration_seconds` renamed to `self._duration` — must update all references**
   - Missed references caused `AttributeError` in dashboard and duration check
   - Fix pattern: grep for all `self.duration_seconds` before rename

### Paper Trading Results (First 5 minutes)

| Position | Side | Entry | Reason |
|---|---|---|---|
| PURR | SHORT | 0.1470 | positive_funding (0.00012061) |
| ZORA | LONG | 0.1089 | negative_funding (-0.00009963) |
| XLM | LONG | 0.2632 | negative_funding (-0.00008723) |

FET, HYPE, VVV were rejected (max concurrent positions = 3).

### Monitoring Pattern

```bash
# Live log
tail -f testnet_logs/paper_bot.log

# Status JSON (updated each cycle)
cat testnet_logs/paper_status.json

# Check bot alive
pgrep -f paper_trading_bot.py

# Trade log (exported on shutdown)
cat testnet_logs/paper_trades.json

# Final report (exported on shutdown)
cat testnet_logs/paper_final_report.json
```

### delegate_task Use Case: Background Installation

The Claude Code CLI installation via `delegate_task` was successful:
- Installed globally with `--prefix /data/.local` (avoids system path permission issue)
- Node v24.15.0 was already available — check before assuming
- npm 11.12.1 worked fine

Pattern: for system-level installs (npm global, CLI tools), use `delegate_task` with `toolsets=['terminal']` to keep main context clean.

### Cron Monitoring Pattern

Created monitoring cron with `cronjob(action='create')`:
- Schedule: `0 */6 * * *` (every 6 hours)
- Checks `pgrep` for liveness + reads `paper_status.json`
- Delivers to `origin` (current session)
- Duration: matches bot run duration (48 hours)
