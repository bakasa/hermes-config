# Research Agent Vault Architecture — 2026-06-02

## Core Insight
A real research agent compounds evidence over time. It does NOT produce disposable digests.
Output ≠ compounding evidence.

## What the Research Agent Must Answer
- What do we know now that we did not know before?
- Which claims are strong vs. interesting but under-evidenced?
- Which sources and topics keep being useful?
- Which signals belong to which agent?
- Which old beliefs are now stale?

## Vault Structure

### Data Layer
- **Findings**: Individual observed signals (from docs, GitHub, feeds, X, search)
- **Claims**: Candidate beliefs extracted from findings, clustered and tracked over time
- **Source Evidence**: Citation trail — URLs, source types, excerpts, timestamps
- **Dossiers**: Living topic files for research lanes (AI agents, frontier AI, crypto rails, memory, robotics, etc.)

### Key Separation
- A finding is NOT a claim
- A claim is NOT verified knowledge
- A source record is NOT a conclusion
- A dossier is NOT a daily summary
- A weak signal is NOT a task

### Operational Detail (Reference Implementation)
- 2,631 claim records
- 2,694 findings
- 2,694 source evidence records
- 13 indexed dossiers
- 18 registered source surfaces
- 8 operational modes in the loop skill
- 6 handoff lanes routing to other agents
- 36 vault tools (validation, compilation, backup, search, health, recovery)
- 6-hour refresh cadence + 3 daily delivery jobs

## Current State (What We Built)
- blogwatcher-cli with 3 active feeds (HF, Import AI, BAIR)
- Cron job: research-agent-daily at 06:00 UTC
- First digest: 2026-06-01.md
- Skills: research-agent SKILL.md, feed-list, search-queries

## What Still Needs Building
- Claims database (SQLite layer on top of findings)
- Source evidence tracking (URL + excerpt + timestamp per finding)
- Dossier system (per-topic living files)
- Stale signal detection (what's no longer true?)
- Handoff routing (which signals go to which agent)
- Vault health tools (validation, backup, recovery)
- 6-hour refresh cadence (not just daily)
