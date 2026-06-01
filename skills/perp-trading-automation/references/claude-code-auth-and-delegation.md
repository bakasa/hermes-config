# Claude Code CLI Auth — Cross-User Setup Patterns

_Last updated: 2026-06-01_

## Problem: OAuth token in root, agent runs as non-root

Claude Code stores credentials in `$HOME/.claude/.credentials.json`. When OAuth login happens in a root shell but the agent runs as `hermes` user, the agent cannot read root's credential files.

### Fix
```bash
# Copy credentials to agent user's home
mkdir -p /data/.claude
cp /root/.claude/.credentials.json /data/.claude/.credentials.json
chown -R hermes:hermes /data/.claude/
```

### Problem: Print mode (`-p`) says "Invalid API key" even when `auth status` says logged in

`claude auth status` can return `loggedIn: true` (reading from credentials file) but `claude -p` still fails with "Invalid API key". This happens because:

- OAuth tokens (browser login) only work in the **interactive TUI** (`claude` without `-p`)
- **Print mode (`-p`)** requires `ANTHROPIC_API_KEY` environment variable

### Fix
```bash
# Get API key from https://console.anthropic.com/settings/keys
export ANTHROPIC_API_KEY="sk-..."
export PATH="/data/.local/bin:$PATH"
claude -p "task here" --allowedTools Read,Edit --max-turns 5
```

### Interactive mode works with OAuth

```bash
# This works with OAuth (no API key needed)
export PATH="/data/.local/bin:$PATH"
HOME=/data claude  # interactive TUI
```

For Hermes agent delegation to Claude Code, use the `claude-code` skill with `acp_command` parameter.

## Config: Approval mode

File: `/data/.hermes/config.yaml`

```yaml
approvals:
  mode: manual    # requires confirmation for every tool execution
  # mode: auto   # executes immediately, no confirmation prompts
```

To switch: edit the file and restart the gateway. Only set `auto` in trusted sandboxed environments.

## Key locations

| Item | Path |
|---|---|
| Claude Code binary | `/data/.local/bin/claude` |
| Credentials | `/data/.claude/.credentials.json` |
| Hermes config | `/data/.hermes/config.yaml` |
| Approval setting | line ~364 of config.yaml |
