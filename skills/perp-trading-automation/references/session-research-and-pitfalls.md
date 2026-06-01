# Perp Trading Bot — Research & Pitfalls Reference

## Session Research Findings (2025-05-31)

### Trust Wallet Agent SDK
- CLI command: `twak` (install: `npm install -g @trustwallet/cli`)
- Auth: HMAC-SHA256 over METHOD + PATH + QUERY + ACCESS_ID + NONCE + DATE
- Credentials stored in `~/.twak/credentials.json` with `0600` permissions
- Available commands init, wallet (create/balance/portfolio/sign-message/keychain), transfer, swap, erc20 (approve/revoke/allowance), price, balance, alert (create/list/check/delete), history, tx
- Developer portal: https://portal.trustwallet.com

### Hyperliquid
- REST API: `https://api.hyperliquid.xyz/info` (read), `https://api.hyperliquid.xyz/exchange` (write)
- Python SDK: `hyperliquid-dex/hyperliquid-python-sdk` v0.23.0, 536 forks, active development
- Funding rates via `{"type": "metaAndAssetCtxs"}` — data[0] = meta (universe = asset names), data[1] = asset contexts (funding, markPx, oraclePx, premium)
- Asset names are NOT in the asset context objects — they are indexed via `universe[i].name` from data[0]
- Rate limit: 1200 req/min per IP
- API wallet model: create separate API wallet at https://app.hyperliquid.xyz/API for order signing

### GMX
- Chains: Arbitrum, Avalanche, Botanix, MegaETH
- Up to 100x leverage, Chainlink oracle pricing
- Typescript SDK: https://github.com/gmx-io/gmx-synthetics (5,844 commits, active)
- Contract interaction: Reader contract for views, Exchange/Position Router for writes

### Aster DEX
- Smart contract based, on EVM chains (Arbitrum/Base)
- API still maturing — placeholder URL `https://api.asterdex.com`
- Monitor official docs for endpoint updates

## Pitfalls Encountered

1. **`pip install` fails without root** — Solution: always use `python3 -m venv .venv` + `source .venv/bin/activate` first
2. **`--user` install also fails** — Python in Docker has user site-packages disabled; virtualenv is the only option
3. **Hyperliquid `coin: None`** — Asset names not in context objects; must index via `universe[i].name` from metadata
4. **`NameError: checkdown`** — Typo in `get_eth_balance`; always run self-test after writing code
5. **No web_search tool available** — Use `browser_navigate` + `browser_snapshot` for research instead

## Key File Locations (Session Output)

| File | Path |
|---|---|
| Core client | `/data/workspace/perp-trading-bot/src/dex_client.py` |
| Config template | `/data/workspace/perp-trading-bot/config/.env.example` |
| Testnet logs | `/data/workspace/perp-trading-bot/testnet_logs/dex_client.log` |
| Agent skill | `/data/.hermes/skills/perp-trading-automation/SKILL.md` |
