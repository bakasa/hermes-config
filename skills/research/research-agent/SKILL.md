---
name: research-agent
description: >
  Research agent with evidence vault. Scans AI landscape, extracts findings,
  tracks claims over time, maintains dossiers, and routes signals to the
  correct agent. Compounds knowledge — does NOT produce disposable digests.
  6-hour refresh cadence + 3 daily deliveries.
trigger_keywords:
  - research scan
  - daily digest
  - ai news
  - what's new
  - scan feeds
  - vault update
  - claims check
---

# Research Agent — Evidence Vault

The research agent is the system's evidence collector. It absorbs noise from the outside world and preserves what matters.

## Core Principle

**A finding is not a claim. A claim is not verified knowledge.**

The vault has space for each stage. Nothing gets flattened into confident prose.

## Vault Structure

```
~/.hermes/research/vault/
├── findings/          # Individual observed signals (one file per finding)
├── claims/            # Candidate beliefs extracted from findings
├── sources/           # Citation trail (URL, type, excerpt, timestamp)
├── dossiers/          # Living topic files
│   ├── ai-agents.md
│   ├── frontier-ai.md
│   ├── crypto-rails.md
│   ├── memory-orchestration.md
│   └── robotics.md
├── handoffs/          # Signals routed to other agents
│   ├── to-subconscious/   # Pattern ideas for the subconscious agent
│   ├── to-main/           # Strategic signals for the main agent
│   ├── to-coder/          # Build-ready signals
│   └── to-qa/             # Quality concerns
└── index.md           # Vault health dashboard
```

## Finding Format

```markdown
# Finding: [short title]
- **Date**: YYYY-MM-DD
- **Source**: [URL]
- **Type**: news | paper | github | x-post | feed | search
- **Excerpt**: [key quote or summary, 1-3 sentences]
- **Tags**: [comma-separated topics]
- **Status**: new | processed | promoted-to-claim | stale
```

## Claim Format

```markdown
# Claim: [statement of belief]
- **Status**: weak | moderate | strong | verified | stale
- **Created**: YYYY-MM-DD
- **Last evidence**: YYYY-MM-DD
- **Confidence**: [low | medium | high]
- **Summary**: [2-3 sentence summary of the evidence]
```

## Dossier Format

```markdown
# Dossier: [topic]
- **Last updated**: YYYY-MM-DD
- **Signal count**: N
- **Summary**: [current state of knowledge on this topic]
- **Open questions**: [what we don't know yet]
- **Stale beliefs**: [what we used to think but no longer hold]
```

## Operational Modes

1. **scan** — Pull new signals from all registered sources
2. **extract** — Process raw signals into structured findings
3. **claim** — Extract candidate beliefs from findings clusters
4. **dossier** — Update living topic files
5. **stale** — Flag findings/claims that are no longer current
6. **route** — Send signals to the right agent (handoffs/)
7. **deliver** — Produce digest for Main agent
8. **health** — Vault integrity check

## Handoff Lanes

| Lane | Destination | What goes there |
|---|---|---|
| to-subconscious | Subconscious agent | Weird patterns, unexpected connections |
| to-main | Main agent (OWL) | Strategic signals, market shifts, major announcements |
| to-coder | Coder agent | Build-ready ideas, new tools/libraries, API changes |
| to-qa | QA agent | Quality concerns, bug reports, broken things |

## Source Surfaces

1. Hugging Face Blog (RSS)
2. Import AI newsletter (RSS)
3. BAIR Blog (RSS)
4. arXiv (cs.AI, cs.LG, cs.CL)
5. Hacker News (top posts)
6. X/Twitter (AI circles)
7. GitHub trending (AI/ML repos)
8. Polymarket (AI markets)
9. TechCrunch AI
10. The Verge AI

## Cron Schedule

- **Every 6 hours** — scan + extract + claim (modes 1-3)
- **Daily 06:00 UTC** — dossier update + stale check + route (modes 4-6)
- **Daily 08:00 UTC** — deliver digest to Main agent (mode 7)
- **Weekly Monday** — health check + vault integrity (mode 8)

## Key Queries the Vault Must Answer

- What do we know now that we did not know before?
- Which claims are strong vs. under-evidenced?
- Which sources and topics keep being useful?
- Which signals belong to which agent?
- Which old beliefs are now stale?

## References

- `references/feed-list.md` — curated AI blogs and news sources
- `references/search-queries.md` — arXiv, web, Polymarket query templates
- `references/vault-architecture.md` — design doc: findings vs claims vs knowledge
- `references/vault-tools.md` — operational modes, lifecycle, routing rules, health checks