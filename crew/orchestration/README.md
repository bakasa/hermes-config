# Crew Orchestration — Multi-Agent Coordination

This is the coordination hub for the Hermes multi-agent crew. It defines how agents communicate, how work flows, and how the system operates as a whole.

## Crew Architecture

```
Research Agent (evidence vault)
    ↓ handoffs/to-subconscious
Subconscious Agent (pattern incubator)
    ↓ insights
Main Agent (OWL) ← you are here
    ↓ assignments
Coder Agent (builds & ships)
    ↓ PRs
QA Agent (reviews & approves)
    ↓ feedback loop → Coder (fixes) or Main (merges)
```

## Agent Roster

| Agent | Role | Trigger | Output |
|---|---|---|---|
| **Research** | Evidence collector | Cron (daily 06:00 UTC) + 6h scan | Findings, claims, dossiers in vault |
| **Subconscious** | Pattern incubator | Cron (4h background) + handoffs | Hypotheses, cross-domain insights |
| **Main (OWL)** | Coordinator | User messages + agent handoffs | Decisions, assignments, responses |
| **Coder** | Builder | Main assignments + research handoffs | PRs, diffs, completion reports |
| **QA** | Quality gate | Coder output | Verdicts, feedback, quality reports |

## Handoff Topology

```
research/vault/handoffs/
├── to-subconscious/    # Weak signals, anomalies, weird patterns
├── to-main/            # Strategic signals, major announcements
├── to-coder/           # Build-ready ideas, new tools/libraries
└── to-qa/              # Quality concerns, bug reports

crew/orchestration/handoffs/
├── from-subconscious/  # Insights routed to Main
├── from-main/
│   ├── to-coder/       # Tasks assigned to Coder
│   └── to-qa/          # Direct QA requests
├── from-coder/
│   ├── to-qa/          # PRs ready for review
│   └── to-main/        # Completions and blockers
└── from-qa/
    ├── to-coder/       # Fix feedback
    └── to-main/        # Quality reports and verdicts

crew/orchestration/completions/
└── from-coder/         # Archived completion reports

crew/orchestration/reports/
└── from-qa/            # Archived quality reports
```

## Activation Rules

### Research Agent
- **Every 6 hours**: scan + extract
- **Daily 06:00 UTC**: claim extraction + stale check + route
- **Daily 08:00 UTC**: deliver digest to Main
- **Weekly (Monday)**: vault health check

### Subconscious Agent
- **Every 4 hours**: passive drift (check for new handoffs, incubate)
- **On-demand**: when Main asks for pattern search or "what if" analysis
- **Route trigger**: when a handoff from Research arrives

### Coder Agent
- **On-demand**: when Main assigns a task or Research routes a build signal
- **Priority order**: (1) bugs from QA, (2) Main assignments, (3) Research build signals

### QA Agent
- **On-demand**: when Coder routes a PR for review
- **Target turnaround**: within one cycle of receipt

### Main Agent (OWL)
- **Always active**: responds to user messages and agent handoffs
- **Orchestrates**: assigns tasks, makes merge decisions, resolves conflicts

## Feedback Loops

### Coder ↔ QA Loop
Coder builds → QA reviews → QA sends fixes back to Coder → Coder fixes → QA re-reviews → SHIP

**Max 3 iterations.** If still not shipping after 3 rounds, escalate to Main.

### Research → Subconscious → Main Loop
Research flags weak signal → Subconscious incubates → Subconscious generates insight → Main decides action

### Research → Coder Direct
Research flags build-ready signal → Coder implements (Main still oversees)

## File Naming Convention

All handoff files follow: `YYYY-MM-DD_descriptive-name.md`

Examples:
- `2026-06-01_openai-gpt5-rumor.md`
- `2026-06-01_fix-auth-bypass.md`
- `2026-06-01_qa-perp-bot-pr42.md`

## State Management

Each agent maintains its own state file:
- `crew/subconscious/index.md`
- `crew/coder/index.md`
- `crew/qa/index.md`

The orchestration hub maintains:
- `crew/orchestration/index.md` — overall crew status
- `crew/orchestration/activity-log.md` — running log of all agent activity

## Communication Protocol

### Handoff Message Format
Every handoff file must include:
```markdown
# [Agent] Handoff: [short title]
- **Date**: YYYY-MM-DD
- **From**: [agent name]
- **To**: [agent name]
- **Priority**: low | medium | high | critical
- **Summary**: [what this is about]
- **Action required**: [what the receiving agent should do]
```

### No Direct Agent-to-Agent Chat
All communication goes through files. Agents read handoff directories. No agent calls another agent directly. This keeps things inspectable and auditable.

## Security

- No agent may access credentials (.env, auth.json)
- No agent may modify Hermes config without Main approval
- No agent may modify another agent's skill without Main approval
- All PRs require QA review before merge
- Main agent has override authority on all decisions
