# Perp Trading Bot — Implementation Reference

_Last updated: 2025-05-31 (v2.0.0)_

## Module Map

| Module | Lines | Purpose |
|---|---|---|
| `src/dex_client.py` | ~470 | EVM RPC client — ETH/ERC-20 balance reads, public Hyperliquid funding rates |
| `src/hyperliquid_client.py` | ~563 | Full Hyperliquid order lifecycle |
| `src/aster_client.py` | ~130 | Aster DEX adapter (structured stub — ABI pending) |
| `src/risk_engine.py` | ~350 | Risk engine with 10-layer validation |
| `src/trading_bot.py` | ~370 | Main orchestrator + CLI + strategy interface |

## HyperliquidClient — Key Implementation Details

### API Wallet Model
Hyperliquid requires a **separate API wallet** for order signing. Create at https://app.hyperliquid.xyz/API.
The main wallet holds funds. The API wallet signs orders. Both must be configured.

### Asset Name Resolution
Asset names are NOT in the `metaAndAssetCtxs` response's asset context objects.
They are in `data[0]["universe"][i]["name"]` and must be matched by index:
```python
universe = data[0].get("universe", [])
for i, ctx in enumerate(data[1]):
    coin = universe[i]["name"] if i < len(universe) else f"asset_{i}"
```

### Signing Scheme
Hyperliquid uses direct ECDSA signing (not EIP-712 for most actions).
The message to sign is `json.dumps(action, separators=(",", ":")) + str(nonce)`,
hashed with `Web3.keccak()`, then signed with the API wallet key.

### Exchange Endpoint Payload
```python
{
    "action": { "type": "order", "orders": [...], "grouping": "na" },
    "nonce": <int milliseconds>,
    "signature": { "r": "0x...", "s": "0x...", "v": 27 or 28 },
    "vaultAddress": None,  # or vault address if using vault
}
```

### Order Object Structure
```python
{
    "a": asset_id,          # int, from universe index
    "b": True,              # True = buy, False = sell
    "p": "73500.0",         # price as string
    "s": "0.01",            # size as string
    "r": False,             # reduce_only
    "t": {"limit": {"tif": "Gtc"}},  # or {"market": {"tif": "Ioc"}}
    "c": "my-cloid",        # optional client order ID
}
```

## RiskEngine — Validation Layers

1. Trading halt check
2. Max position size
3. Max leverage
4. Daily loss limit → halt
5. Max concurrent positions
6. Max total exposure
7. Max consecutive losses → halt
8. Max funding rate
9. Circuit breaker drawdown → halt
10. Sufficient margin

## Aster DEX Status
- Runs on Aster Chain (own L1, 100k+ TPS, 50ms blocks)
- API: https://api.asterdex.com (endpoints TBC)
- Smart contract addresses: NOT YET PUBLIC — update aster_client.py when docs publish
- Bridging: Arbitrum/Base → Aster Chain requires a bridge contract (not implemented)

## Environment Notes

- `pip install` fails on system Python (no root): always use `python3 -m venv .venv`
- `--user` flag also fails: user site-packages disabled in container
- Public RPCs can be flaky: implement retry with exponential backoff for production
- Hyperliquid rate limit: 1200 req/min per IP
