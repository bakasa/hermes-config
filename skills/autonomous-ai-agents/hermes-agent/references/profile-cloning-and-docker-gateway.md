# Profile Cloning & Docker Gateway Constraints

## `hermes profile create` — Clone Flags

| Flag | What it copies | When to use |
|------|---------------|-------------|
| `--clone` | `config.yaml`, `.env`, `SOUL.md` only | Fresh profile, new API keys, same base personality |
| `--clone-all` | Full profile: config, `.env`, `auth.json`, `SOUL.md`, skills, state.db, cron, sessions, models cache | Duplicate an existing setup (e.g., prod → staging, default → project-specific) |
| `--clone-from SOURCE` | Same as above, but from a named profile instead of the active one | Clone a non-default source |
| (no flag) | Empty profile, no config or keys | From-scratch setup |

`--clone-all` copies `auth.json` including credential pool state — including **exhaustion markers**. After cloning, check `~/.hermes/profiles/<name>/auth.json` for `"last_status": "exhausted"` and reset with `hermes auth reset <provider>` if needed.

### Confirm interactive prompt

`hermes profile delete <name>` requires typing the profile name to confirm. In non-interactive contexts, pipe it:

```bash
echo "<name>" | hermes profile delete <name>
```

---

## Docker Container Gateway Constraint

**A Docker container runs exactly one Hermes gateway process.** The default gateway is the container's main supervised process. Running a second profile's gateway in the same container requires either a new container or the `--no-supervise` flag (with trade-offs).

### The supervisord gateway (Docker images)

The Docker image uses **supervisord** (not systemd) as the process supervisor. The gateway runs as a managed `[program:gateway]` in `/etc/supervisord.conf`. Key implications:

1. **`hermes gateway start` errors with:**
   ```
   Service start is not applicable inside a Docker container.
   The gateway runs as the container's main process.
   ```

2. **Running as `hermes` user (not root):**
   - Container UID/GID is typically `10000:10000` (`hermes`)
   - `sudo` is not available
   - `/etc/supervisord.conf` is owned by root — cannot be modified by `hermes` user
   - `supervisorctl` requires root permissions

3. **Cannot add a second supervised program for a cloned profile without root:**
   - Modifying `/etc/supervisord.conf` requires root
   - `supervisorctl` add/update commands require root
   - Workaround: run the second gateway with `--no-supervise` as a background process (see below)

### Running a second profile's gateway with `--no-supervise`

To run a cloned profile's gateway **alongside** the default supervisor-managed gateway inside the same container, use the `--no-supervise` flag. This bypasses the s6/supervisor redirect and runs the gateway as a plain foreground process.

**Via CLI wrapper:**
```bash
dev-house gateway run --no-supervise
```

**Via Python `execute_code` (fully detached):**
```python
import subprocess, os
env = os.environ.copy()
env["HOME"] = "/data"
env["HERMES_HOME"] = "/data/.hermes/profiles/<name>"
# Source profile .env for API keys into env dict, then:
subprocess.Popen(
    ["dev-house", "gateway", "run", "--no-supervise"],
    stdout=open("/data/.hermes/profiles/<name>/gateway.log", "w"),
    stderr=subprocess.STDOUT,
    env=env, cwd="/data", start_new_session=True,
)
```

**Trade-offs of `--no-supervise`:**
- ✅ Runs alongside the default gateway in the same container
- ✅ Process survives gateway restarts
- ❌ No auto-restart on crash (unlike supervised process)
- ❌ No lifecycle management or stdout capture via supervisor
- ❌ Will be killed if the container restarts

### HERMES_HOME override for profile gateway wrapper script

Write a wrapper script that sources the profile `.env` and sets `HERMES_HOME`:

```bash
#!/bin/bash
export HOME="/data"
export HERMES_HOME="/data/.hermes/profiles/<name>"
set -a
source /data/.hermes/profiles/<name>/.env
set +a
exec python3 -c "from hermes_cli.gateway import run_gateway; run_gateway()"
```

**Do NOT set `HERMES_PROFILE`** — the gateway entrypoint does not recognize this env var. Profile selection is driven by `HERMES_HOME` pointing to the profile directory.

### Workarounds summary

| Approach | How | Limitations |
|----------|-----|-------------|
| **New container** (recommended for production) | New Docker/Railway service entrypoint: `hermes --profile <name> gateway run` | Requires infra access to provision |
| **`--no-supervise` background** | `dev-house gateway run --no-supervise` | No auto-restart; killed on container restart |
| **Subagents** | Use `delegate_task` inside the running container for parallel workstreams | Not persistent; no independent Slack/Discord channel |
| **Switch this container** | Stop default gateway, restart with `--profile <name>` | Replaces — loses this session and its gateway connection |

---

## Slack Platform: Requires Separate Bot Per Gateway

**Each Hermes gateway connecting to Slack needs its own Slack Bot App with unique tokens.** You cannot share a single `SLACK_BOT_TOKEN` / `SLACK_APP_TOKEN` pair between two gateways in the same workspace. If you try, only one gateway will receive events; the other will log "No messaging platforms enabled."

### Token variants — what you need

| Token | Env var | Pattern | Purpose |
|-------|---------|---------|---------|
| **Bot Token** | `SLACK_BOT_TOKEN` | `xoxb-...` | OAuth bot identity; sends messages, reads channels |
| **App Token** | `SLACK_APP_TOKEN` | `xapp-...` | App-level token for Socket Mode (real-time events) |

**Do NOT confuse** with `SLACK_REFRESH_TOKEN` / `SLACK_USER_TOKEN` — those are user-level OAuth tokens (for the Slack CLI / workflow runner), and the Hermes gateway does **not** use them.

### Creating a second Slack bot for a cloned profile

1. Go to https://api.slack.com/apps → **Create New App** → From Scratch
2. **Basic Information** → generate an **App-Level Token** (`xapp-`) with `connections:write` scope → enables Socket Mode
3. **OAuth & Permissions** → add bot scopes: `chat:write`, `app_mentions:read`, `channels:history`, `groups:history`, `im:history`, `im:read`, `im:write`, `users:read`, `files:read`, `files:write`
4. **Event Subscriptions** → enable and subscribe to: `message.im`, `message.channels`, `message.groups`, `app_mention`
5. Install the app to your workspace
6. Add the tokens to the profile's `.env`:
   ```bash
   echo 'SLACK_BOT_TOKEN=*** >> /data/.hermes/profiles/<name>/.env
   echo 'SLACK_APP_TOKEN=*** >> /data/.hermes/profiles/<name>/.env
   echo 'SLACK_HOME_CHANNEL=<channel-id>' >> /data/.hermes/profiles/<name>/.env
   ```

### `config.yaml` Slack section requirement

Even with correct env vars, the cloned profile's `config.yaml` must have a `slack:` section for the gateway to enable the platform. After cloning, verify the section is present — if missing, add:

```yaml
slack:
  require_mention: true
  free_response_channels: ''
  allowed_channels: ''
  channel_prompts: {}
```

The actual bot/app tokens come from environment variables, not `config.yaml`. The `slack:` section just tells the gateway to enable the platform.

---

## Workspace Files in Cloned Profiles

After cloning a profile, write `SOUL.md`, `USER.md`, and `MEMORY.md` to the profile's own directory. Use `cross_profile=true` to bypass the guard that prevents editing another profile's files:

```python
write_file(
    path="/data/.hermes/profiles/<name>/SOUL.md",
    content="...",
    cross_profile=True
)
```

Do NOT rely on root-level `/data/USER.md` or `/data/MEMORY.md` — profile-scoped files live under the profile directory.

---

## Wrapper Script PATH Issue

`hermes profile create` generates a wrapper at `~/.local/bin/<name>` but prints a warning that `~/.local/bin` is not in PATH. In Docker containers this is almost always the case.

Fix per-command:

```bash
export PATH="$HOME/.local/bin:$PATH"
dev-house gateway status
```

Or permanently add to `~/.bashrc` / `~/.zshrc` inside the container.

---

## Typical Workflow: Clone Default → Project Profile

```bash
# 1. Clone everything from default
hermes profile create my-project --clone-all --description "Project X dev agent"

# 2. Write profile-scoped personality/context files
#    Use write_file(path=..., cross_profile=True) for:
#    - ~/.hermes/profiles/my-project/SOUL.md  (personality, operational protocols)
#    - ~/.hermes/profiles/my-project/USER.md  (developer preferences scaffold)
#    - ~/.hermes/profiles/my-project/MEMORY.md (project tracker, conventions)

# 3. Fix PATH
export PATH="$HOME/.local/bin:$PATH"

# 4. Verify auth state (cloned credentials may be exhausted)
cat ~/.hermes/profiles/my-project/auth.json | python3 -c \
  "import sys,json; d=json.load(sys.stdin); [print(p['id'], p.get('last_status','?')) for p in d.get('credential_pool',{}).get('openrouter',[])]"

# 5. If connecting to Slack, create a new Slack bot app and add tokens to .env

# 6. Start
#    For a second gateway in the same container:
#    dev-house gateway run --no-supervise
#    For a new container (recommended for production):
#    hermes --profile my-project gateway run
```

---

## auth.json Exhaustion Semantics

When a cloned profile's API key shows `"last_status": "exhausted"` with `"last_error_code": 402`:

- The credential pool will skip exhausted keys automatically
- If ALL keys are exhausted, every model call fails with 402
- Reset exhaustion: `hermes auth reset <provider>`
- Add more keys: `hermes auth add <provider>` (rotates automatically)
