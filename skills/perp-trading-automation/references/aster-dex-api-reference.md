# Aster DEX Futures API — Quick Reference

## Base URLs

| Service | URL |
|---|---|
| REST API | `https://fapi.asterdex.com` |
| WebSocket | `wss://fstream.asterdex.com` |

**CRITICAL**: The old stub used `https://api.asterdex.com` — that is WRONG. All Futures API calls go to `fapi.asterdex.com`.

## Auth: HMAC SHA256 (not EIP-712)

Aster uses standard HMAC SHA256 signing (like Binance), NOT Hyperliquid's EIP-712 typed data signing.

```
signature = HMAC_SHA256(secret_key, query_string)
```

Where `query_string` is the sorted params concatenated with `&`, including `timestamp` and `recvWindow`.

## Symbol Format

- Aster: `"BTCUSDT"`, `"ETHUSDT"`, `"AAPLUSD"`, `"TSLAUSDT"`
- Hyperliquid: `"BTC"`, `"ETH"`
- **Always use `get_funding_rates_normalized()`** to get `"coin": "BTC"` format for strategy code

### Suffix Stripping Pattern

Some markets end in `"USDT"`, others in `"USD"` (e.g. `AAPLUSD`). Use `endswith()` not `replace()`:

```python
# CORRECT — only strips true suffixes
coin = symbol
for suffix in ("USDT", "USD"):
    if symbol.endswith(suffix) and len(symbol) > len(suffix):
        coin = symbol[: -len(suffix)]
        break

# WRONG — replace() corrupts symbols containing USDT/USD mid-string
coin = symbol.replace("USDT", "").replace("USD", "")
```

## Key Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/fapi/v1/premiumIndex` | GET | No | Mark price + funding rate for all symbols |
| `/fapi/v1/fundingRate` | GET | No | Historical funding rates |
| `/fapi/v1/depth` | GET | No | Orderbook (L2) |
| `/fapi/v1/klines` | GET | No | Candlestick data |
| `/fapi/v1/ticker/24hr` | GET | No | 24hr price statistics |
| `/fapi/v1/exchangeInfo` | GET | No | Symbol info, filters, rate limits |
| `/fapi/v1/order` | POST | Yes (signed) | Place order |
| `/fapi/v1/order` | DELETE | Yes (signed) | Cancel order |
| `/fapi/v1/allOpenOrders` | DELETE | Yes (signed) | Cancel all orders |
| `/fapi/v1/openOrders` | GET | Yes (signed) | Query open orders |
| `/fapi/v1/allOrders` | GET | Yes (signed) | Query all orders |
| `/fapi/v2/balance` | GET | Yes (signed) | Account balance |
| `/fapi/v4/account` | GET | Yes (signed) | Full account info + positions |
| `/fapi/v2/positionRisk` | GET | Yes (signed) | Position risk |
| `/fapi/v1/leverage` | POST | Yes (signed) | Change leverage |
| `/fapi/v1/marginType` | POST | Yes (signed) | Change margin type |
| `/fapi/v1/positionSide/dual` | POST | Yes (signed) | Change position mode |
| `/fapi/v1/userTrades` | GET | Yes (signed) | Trade history |
| `/fapi/v1/income` | GET | Yes (signed) | Income history (funding, commissions, PnL) |
| `/fapi/v1/batchOrders` | POST | Yes (signed) | Place multiple orders (max 5) |

## Rate Limits

| Type | Limit |
|---|---|
| Request weight | 2400 per minute |
| Orders | 1200 per minute (per account) |
| Orders (10s window) | 300 per 10 seconds |

Response header `X-MBX-USED-WEIGHT-1M` shows current usage.

## Market Data Response Format (premiumIndex)

```json
{
  "symbol": "BTCUSDT",
  "markPrice": "71790.30000000",
  "indexPrice": "71785.12345678",
  "estimatedSettlePrice": "71780.00000000",
  "lastFundingRate": "0.00010000",
  "interestRate": "0.00010000",
  "nextFundingTime": 1780329600000,
  "time": 1780319820000
}
```

## Order Placement Parameters

Required for all orders: `symbol`, `side` (BUY/SELL), `type`, `quantity`, `timestamp`, `signature`

Common `type` values: `LIMIT`, `MARKET`, `STOP`, `STOP_MARKET`, `TAKE_PROFIT`, `TAKE_PROFIT_MARKET`, `TRAILING_STOP_MARKET`

For LIMIT: also need `price` and `timeInForce` (GTC/IOC/FOK/GTX)
For STOP/TAKE_PROFIT: also need `stopPrice`
For TRAILING_STOP_MARKET: also need `callbackRate` (0.1-5.0, where 1 = 1%)

## Position Response Format

```json
{
  "symbol": "BTCUSDT",
  "positionAmt": "0.01",
  "entryPrice": "71000.0",
  "markPrice": "71790.3",
  "unrealizedProfit": "7.903",
  "leverage": "3",
  "marginType": "cross",
  "positionSide": "BOTH",
  "liquidationPrice": "0.0"
}
```

## Income Types

`TRANSFER`, `WELCOME_BONUS`, `REALIZED_PNL`, `FUNDING_FEE`, `COMMISSION`, `INSURANCE_CLEAR`, `MARKET_MERCHANT_RETURN_REWARD`

## Unique Aster Markets

Aster supports stock perps and other non-crypto markets:
- `TSLAUSDT`, `AAPLUSDT`, `AAPLUSD`, `AMZNUSDT`, `GOOGLUSDT`, `MSFTUSDT`, `METAUSDT`, `NVDAUSDT`
- `SHIELDTSLAUSDT`, `SHIELDAMZNUSDT` (Shield Mode variants)
- Chinese-named markets: `我踏马来了USDT`, `老子USDT`, `雪球USDT`, etc.

Total: **602 markets** (as of 2026-06-01).

## API Key Setup

1. Create API key at https://app.asterdex.com
2. Set env vars: `ASTER_API_KEY` and `ASTER_API_SECRET`
3. Or pass directly: `AsterClient(api_key="...", api_secret="...")

## Common Errors

| Code | Message | Fix |
|---|---|---|
| -1121 | Invalid symbol | Check symbol format (e.g. "BTCUSDT" not "BTC") |
| -2010 | NEW_ORDER_REJECTED | Check filters (min price, min qty, etc.) |
| -2021 | Order would immediately trigger | Adjust stopPrice/activationPrice |
| -2022 | ReduceOnly Order rejected | Position already closed or wrong side |
| 400 | Bad Request | Check params — some symbols need exact format |
| 429 | Rate limit | Back off, use WebSocket for streaming |
| 418 | IP banned | Stop sending requests, wait |
