Claude Code (2026-06-01): SDK+OAuth only method that works in Docker. Clear ANTHROPIC_API_KEY. Wrapper: scripts/claude_delegate.py. Always model=sonnet, bypassPermissions. Delegate ALL logic-heavy tasks. remote-control and -p don't work.

Perp bot v2.1 (2026-06-01): $100 capital, 0.003% entry, $2M vol, 4% stop, relaxed EMA20 (>2% deviation). v2.0 too idle. Self-improvement authorized. Bot running.

Approval: auto.
§
Key skill updates applied after 2026-06-01 paper trading session: (1) perp-trading-automation v3.0 — added paper trading section, FundingRateStrategy docs, background launch pattern, monitoring cron pattern, `dayNtlVlm` volume field pitfall, risk engine seeding requirement; new reference file `references/paper-trading-research-and-pitfalls.md` captures all paper trading pitfalls. (2) dev-house-ops — added `delegate_task` for background installations pattern, added "Don't background-launch silent bounded tasks" pitfall to the skill's pitfalls list.
§
[2026-06-01] User requested a plan for an Uber-style ride-hailing app targeting South African market. Tech stack: Svelte (UI + mobile), .NET backend, Docker deployment to Railway.