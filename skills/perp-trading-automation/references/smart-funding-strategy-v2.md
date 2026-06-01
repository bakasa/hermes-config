# Smart Funding Arbitrage v2 — Strategy Research & Design Notes

## Why v1 Lost Money

The v1 bot (FundingRateStrategy) lost ~3% in 3 hours because:

1. **Entry threshold too low (0.001%)** — Opened positions on tiny funding differences that were just noise. Each trade lost more in spread/slippage than it gained from funding.
2. **No trend filter** — Went long on crashing assets (ZORA) because funding was negative, but price kept falling. Negative funding often coincides with sell pressure.
3. **Tight stops (1%)** — At 3x leverage, 1% stop = 3% equity loss per stop. Normal volatility triggered stops repeatedly.
4. **No spread filter** — Took positions in PURR and ZORA with wide bid-ask spreads that ate profits.

## v2 Design Principles

### 1. Quality Over Quantity
- Entry threshold: **0.003% (3 bps)** — Only trade extreme funding. Was 0.005% in v2.0, lowered to 0.003% in v2.1 after observing only 2 markets passing filters (too restrictive for current conditions).
- Reduces trade frequency but each trade has better risk/reward.

### 2. Trend Alignment (EMA20) — RELAXED in v2.1
- **v2.0 (strict)**: Long only above EMA20, short only below. Blocked many valid signals.
- **v2.1 (relaxed)**: Only block if price is **>2% away from EMA20** against trend. Primary signal is funding rate, not trend. Only avoid strong counter-trend entries.
  - Long: only block if price is >2% BELOW EMA20 (strong downtrend)
  - Short: only block if price is >2% ABOVE EMA20 (strong uptrend)
- Rationale: Mean-reversion in funding is the edge; trend is secondary. Strong (>2%) counter-trend moves can accelerate and hurt.

### 3. Market Quality Filters
- **$2M minimum 24h volume** (lowered from $5M in v2.0). With $5M, only 2-3 markets qualified at any time, leaving the bot idle for hours.
- 0.5% max bid-ask spread as direct transaction cost filter.
- Eliminates ~70% of HL markets (down from ~85% with $5M filter).

### 4. Funding Rate History
- Compare current rate to 8-sample rolling average.
- Only trade if current is 2x the average (spike, not drift).

### 5. Position Sizing for $100 Capital
- $10-15 per position (10-15% of capital).
- Max 2 positions (concentrated, not diluted).
- 3x leverage.
- **4% stop loss** (widened from 3% in v2.0 after PUMP long was stopped out at 3% — volatile alts need more room).
- 3% take profit.

### 6. Exit Signals (Priority Order)
1. Funding flip (sign changes against position — thesis broken).
2. Take profit at 3% unrealized.
3. Stop loss at -4% unrealized.
4. Funding reversion (near zero).

## Version Tuning History

| Version | Entry Threshold | Min Volume | Stop Loss | Trend Filter | Result |
|---------|----------------|------------|-----------|-------------|--------|
| v1.0 | 0.001% | $1M | 1% | None | Lost 3% in 3h — too aggressive |
| v2.0 | 0.005% | $5M | 3% | Strict (price vs EMA) | Too idle — only 2 markets passed filters in 3h |
| **v2.1** | **0.003%** | **$2M** | **4%** | **Relaxed (>2% deviation)** | Active from first cycle — JTO LONG, NEAR LONG opened immediately |

## Known Pitfalls
- PriceRateHistory type hint must be PriceHistory (NameError otherwise).
- EMA20 warmup needs 20 samples (~10 min at 30s interval), filter passes during warmup.
- Funding history window is 8 samples, scale proportionally with poll interval.
- **Stop loss on volatile micro-caps**: PUMP stopped out at 3%. Wider stop (4%) or avoid sub-$1M market cap entirely.

## Future Improvements
- Dynamic sizing: bigger positions for more extreme funding.
- Multi-timeframe EMA: EMA50 for direction, EMA20 for timing.
- Volatility-adjusted stops using ATR instead of fixed percentage.
- Correlation filter to avoid correlated pairs (BTC + ETH).
- Time-of-day filter (funding extremes during low-liquidity hours).
- Per-market max position size based on actual order book depth.
