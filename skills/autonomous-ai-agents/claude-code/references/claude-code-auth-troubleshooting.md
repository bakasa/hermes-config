# Claude Code Auth Troubleshooting

## Auth Status Mismatch Between Sessions

**Symptom:** User reports they logged into Claude Code, but `claude auth status` from the agent's process shows `loggedIn: false`.

**Cause:** Auth credentials are stored per-user in `~/.claude/.credentials.json`. If the agent runs as a different user, or the HOME directory differs, the token won't be visible.

**Diagnosis steps (ask user to run from their shell):**
```bash
claude auth status
echo $HOME
echo $ANTHROPIC_API_KEY
ls -la ~/.claude/.credentials.json 2>/dev/null || echo "no credentials file"
```

**Fixes:**
1. If credentials file exists but is owned by a different user: `sudo chown -R $(whoami) ~/.claude/`
2. If using API key: ensure `ANTHROPIC_API_KEY` is set in the agent's environment  
3. If OAuth token expired: `claude auth login` again from the agent's context

## Quick Print Mode Test

After confirming auth, verify the agent can use Claude Code:
```bash
export PATH="/data/.local/bin:$PATH"
claude -p "Say hello in one sentence" --max-turns 1
```

If this returns a response, auth is working from the agent's context.
