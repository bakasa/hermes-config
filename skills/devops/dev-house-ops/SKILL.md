---
name: dev-house-ops
description: "Lead Engineer & Shop Foreman operational protocol for the dev house. Handles any software task: research, build, test, deploy. Use when the user sends a feature request, bug ticket, or software idea. Enforces Ship Report format, parallel sub-agent decomposition, Docker sandboxing, and skill consolidation after complex work."
---

# Dev House Ops — Lead Engineer & Shop Foreman

Operational protocol for the dev house. Active for ALL software tasks unless explicitly overridden.

## Trigger Conditions

- Any feature request, bug ticket, software idea, or build task received via Slack/messaging.
- Any request to "create", "build", "fix", "deploy", "research" software.

## Operational Protocols

### 1. Context Loading (ALWAYS)
Before writing any code:
- Read `USER.md` — developer's coding preferences, framework choices, naming styles.
- Read `MEMORY.md` — active project tech stack, directory structures, environment configs.
- Read `PROJECTS.md` — active project backlog (if task relates to an active project).

### 2. Parallelization & Workspace Hardening
- Decompose broad software tasks into modular chunks.
- Use `delegate_task` to spawn isolated sub-agents for parallel workstreams (max 3 concurrent examples:
  - Backend route creation + test suite drafting
  - Research (multiple topics) + architecture design
  - Frontend components + integration tests
- ALL execution, dependency installation, and testing must happen inside the Docker/container sandbox.
- Never touch the base host machine.
- Keep the main context window clean — offload work to sub-agents when tasks would exceed ~30% context.

### 3. Asynchronous Task Execution
- Acknowledge the task immediately with a brief confirmation.
- Execute to completion (research → build → test → report).
- Report back with the structured Ship Report.

### 4. Ship Report Format (MANDATORY)
Every deliverable must use this exact layout:

```
■ [PROJECT STATUS]: (Success / Blocks Encountered)
■ [CODE DEPLOYED]: (Brief, scannable markdown list of exact files created or modified)
■ [TEST SUITE VERIFICATION]: (Pass/fail log details from test run)
■ [SKILL CONSOLIDATION]: (New/updated SKILL.md or "None this cycle")
```

### 5. Skill Consolidation (ALWAYS)
After completing a complex or multi-step task (5+ tool calls, non-trivial debugging, or new workflow discovered):
- Document the solution as a Skill Document under the `agentskills.io` layout.
- Ask the user: "Save this as a skill?"
- If confirmed, create via `skill_manage(action='create')`.

## Project Board

Active project backlog is maintained at `/data/PROJECTS.md`. Board format:
- Each project has: ID, Summary, Tech Stack, Architecture, Phased Task Backlog, Key Risks, Dependencies.
- Tasks are tracked by phase: Phase 0 (Research/Setup) → Phase N (Deployment).
- Status markers: ⚪ TODO | 🔄 IN PROGRESS | ✅ DONE | 🔴 BLOCKED.

When a new project is requested:
1. Research the domain (parallel sub-agents if broad).
2. Propose a tech stack and architecture.
3. Create the phased backlog in `PROJECTS.md`.
4. Wait for green light before executing.

## Key File Locations

| File | Purpose |
|---|---|
| `/data/USER.md` | Developer coding preferences |
| `/data/MEMORY.md` | Active projects, tech stack, conventions |
| `/data/PROJECTS.md` | Project backlog board |
| `/data/workspace/` | Active project code area |

## SA Market Defaults

When building for South Africa, consult `references/sa-market-tech-choices.md` for default tech choices (WinSMS, Paystack, Mapbox, etc.) and market non-negotiables (cash payments, offline-first, safety features, multi-language).

## Runtime Environment Constraints (Docker Container)

The agent runs inside a Docker container spawned by Railway. Key constraints:

- **Single main process**: The container's main process IS the running gateway. You cannot start a second independent Hermes gateway profile inside the same container.
- **No root / no sudo**: Running as `hermes` (uid 10000). Cannot modify `/etc/`, cannot use `supervisorctl`, cannot `pip install` to system paths.
- **Use virtualenv**: Always `python3 -m venv .venv && source .venv/bin/activate` before `pip install`.
- **Slack bot app token is exclusive**: One Slack Socket Mode connection per bot app. Two gateways cannot share the same `SLACK_APP_TOKEN`. A second gateway needs its own Slack app.
- **Hermes profile isolation ≠ agent isolation**: Creating a new profile (`hermes profile create`) gives separate config/sessions but does NOT give a separate running agent in the same container. True isolation = separate container.

### delegate_task for Background Work (NEW)

`delegate_task` is ideal for:
- System-level installations (npm global, CLI tools, Docker setup) — keeps main context clean
- Long-running bounded tasks that should not block the main session
- Independent research subtasks

Example pattern from session (Claude Code CLI install):
```python
delegate_task(
    goal="Install Claude Code CLI via npm. Check node/npm available first. "
         "Use --prefix /data/.local if system path not writable. "
         "Verify with claude --version.",
    toolsets=["terminal"]
)
```

**Key pattern:** spawn sub-agent for installs, verify result via summary (includes binary path + version), then integrate in main session.

### User Correction Pattern (DO NOT REPEAT)

When the user asks to "create another agent" or "spin up a separate instance":
1. **FIRST** clarify: Do they mean a separate running process, or just a separate role/persona in the current session?
2. **DEFAULT to "same session, new role"** unless they explicitly confirm they want a new container/profile.
3. **DO NOT** immediately attempt `hermes profile create` + `dev-house gateway start` — this path has 3 hard blockers in container environments (no root, single process, Slack token conflict).
4. **Explain blockers honestly** before attempting, not after hitting them.

## Pitfalls to Avoid

- **Don't skip the Ship Report** — every task, even small ones, gets the full format.
- **Don't hardcode credentials** — use Docker secrets / `.env` with `0600` permissions.
- **Don't mainnet-deploy without explicit user confirmation** — always run paper/live testnet first.
- **Don't start coding without reading USER.md and MEMORY.md first** — the user has preferences.
- **Don't attempt privileged operations** (systemd, supervisorctl, system pip) inside the container — use virtualenv and user-space alternatives.
- **Don't assume two gateways fit in one container** — they don't. One container = one gateway = one Slack app token.
- **Don't skip the Ship Report** — every task, even small ones, gets the full format.
- **Don't hardcode credentials** — use Docker secrets / `.env` with `0600` permissions.
- **Don't mainnet-deploy without explicit user confirmation** — always run paper/live testnet first.
- **Don't start coding without reading USER.md and MEMORY.md first** — the user has preferences.
- **Don't background-launch silent bounded tasks** — `terminal(background=true)` without `notify_on_complete=true` means you WILL forget about the task. Either set `notify_on_complete=true` or set up an external monitor (cron + log tailing) before launching.
- **Don't create a new profile when the user asks for "another agent"** — default to "same session, new role". Only create a new profile/container when they explicitly confirm that's what they want.
- **Don't use `patch` with insufficient context** — when the `old_string` isn't unique enough in the file, `patch` (mode=replace) can silently append at EOF instead of replacing inline. Always include 2-3 surrounding lines of context, and verify the file tail after patching to catch stray content. If patch produces a duplicate or misplaced block, use `execute_code` with Python string replace for surgical fixes.
