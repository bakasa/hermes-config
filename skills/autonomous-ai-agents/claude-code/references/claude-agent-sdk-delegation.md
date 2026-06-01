# claude-agent-sdk Delegation Pattern

## Overview

The `claude-agent-sdk` Python library provides programmatic access to Claude Code without needing tmux or print mode. This is the **recommended approach** for Hermes agents.

## Critical Env Var Gotcha

`ANTHROPIC_API_KEY` must be **unset** before using the SDK with OAuth. If set to the OAuth access token (which happens automatically after `claude auth login`), SDK gets HTTP 401 "Invalid API key".

```python
import os
env = os.environ.copy()
env.pop("ANTHROPIC_API_KEY", None)
os.environ.update(env)
```

## Basic Usage

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient
import asyncio

async def delegate(task, model="sonnet", cwd="."):
    options = ClaudeAgentOptions(
        model=model,
        permission_mode="bypassPermissions",
        cwd=cwd,
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query(task)
        async for msg in client.receive_response():
            if hasattr(msg, "content") and msg.content:
                for block in msg.content:
                    if hasattr(block, "text") and block.text:
                        print(block.text)
```

## User Preferences (always apply)

- **Model:** `sonnet` (always, per user directive)
- **Permissions:** `bypassPermissions` (auto-approve all tools)
- **Delegate all logic-heavy coding tasks to Claude Code** — strategy improvements, bug fixes, new features, refactoring, complex debugging. Simple one-liner changes can be done directly.

## Why Not Other Approaches?

| Approach | Problem |
|---|---|
| `claude -p` (print mode) | Requires `ANTHROPIC_API_KEY` (real API key, not OAuth token). OAuth tokens cause 401. |
| `claude` + tmux | Tmux server won't persist in Docker containers. Server daemonizes and loses parent process. |
| `claude remote-control` | Requires workspace trust dialog (TUI-only, can't automate in Docker). Also needs trust per-directory. |
| SDK + OAuth | Works. No trust dialog needed. No tmux needed. Handles PTY internally. |

## Troubleshooting

| Symptom | Fix |
|---|---|
| HTTP 401 "Invalid API key" | `unset ANTHROPIC_API_KEY` — the OAuth token is not a valid API key |
| CLINotFoundError | `export PATH="/data/.local/bin:$PATH"` |
| Workspace not trusted | SDK bypasses this check automatically |
| Credentials in wrong home | Copy `$HOME/.claude/.credentials.json` to agent's home dir |
