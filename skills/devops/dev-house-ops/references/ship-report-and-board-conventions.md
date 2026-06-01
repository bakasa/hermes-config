# Ship Report & Project Board Reference

## Ship Report Template

Every task deliverable uses this exact format:

```
■ [PROJECT STATUS]: (Success / Blocks Encountered)
■ [CODE DEPLOYED]:
  - /path/to/file.ext  — brief description
  - /path/to/file2.ext — brief description
■ [TEST SUITE VERIFICATION]:
  test_file.py: 12 passed, 0 failed
  OR: N/A — documentation/planning phase only
■ [SKILL CONSOLIDATION]:
  Created/updated: skill-name
  OR: None this cycle
```

## Project Board Conventions (PROJECTS.md)

### Project Entry Structure
```
### PRJ-NNN — Project Name
| Field | Value |
|---|---|
| **Status** | 🔵 QUEUED |
| **Priority** | P1 / P2 / P3 |
| **Created** | YYYY-MM-DD |

#### Tech Stack Table
| Layer | Technology | Rationale |

#### Task Backlog (per phase)
| ID | Task | Status | Notes |
```

### Status Markers
- ⚪ TODO — not started
- 🔄 IN PROGRESS — actively being worked
- ✅ DONE — complete
- 🔴 BLOCKED — waiting on dependency
- 🔵 QUEUED — planned, not yet started

### Priority Levels
- P1 — Critical / blocking other work
- P2 — Important, scheduled
- P3 — Nice to have, backlog

## Sub-Agent Delegation Pattern

Use `delegate_task` for parallel workstreams. Example decomposition for a full-stack feature:

```
tasks: [
  { goal: "Build backend API routes", context: "...", toolsets: ["terminal", "file"] },
  { goal: "Write test suite", context: "...", toolsets: ["terminal", "file"] },
  { goal: "Build frontend components", context: "...", toolsets: ["terminal", "file"] }
]
```

Max 3 concurrent children. All run in isolated terminal sessions.
