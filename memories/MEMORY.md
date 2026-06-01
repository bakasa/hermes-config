[2026-06-01] User requested a plan for an Uber-style ride-hailing app targeting South African market. Tech stack: Svelte (UI + mobile), .NET backend, Docker deployment to Railway.
§
Railway container runs as non-root user 'hermes' (uid 10000). sudo not installed, cannot install at runtime. Shell has zero capabilities. Fix: add sudo to Dockerfile apt packages and configure NOPASSWD.
§
Claude Code CLI located at /data/.local/bin/claude. Print mode (-p) needs ANTHROPIC_API_KEY env var. Interactive TUI works with OAuth only.
§
GitHub: username=bakasa, repos prefixed with hermes-, PAT configured for gh CLI auth. 3 repos pushed: hermes-perp-trading-bot (16 files), hermes-config (600 files), hermes-dev-house (5 files). GITHUB_TOKEN in .env. Always use gh CLI for GitHub operations (not raw git/curl).
§
Claude Code (cc) model routing: --model opus = reviewer/oracle, --model sonnet = coder (default), --model haiku = trivial worker. All via python3 scripts/claude_delegate.py which wraps claude-agent-sdk with OAuth.
§
Hermes Skills Hub: http://hermes-agent.nousresearch.com/docs/skills/ — official Nous Research marketplace with hundreds of skills. Search via `hermes skills search`, install via `hermes skills install`. Categories: creative, dev tools, research, productivity, etc.
§
cc = Claude Code CLI. Model routing: opus=reviewer/oracle, sonnet=coder, haiku=worker. Via python3 scripts/claude_delegate.py "task" --model [opus|sonnet|haiku].
§
Crew: Main(OWL), Subconscious, Research, Coder(cc), QA. Workflow: Research→Subconscious→Main(PRD)→Coder→QA→pass/fail loop. cc=/data/.local/bin/claude, OAuth, ANTHROPIC_API_KEY must unset for SDK. GitHub: bakasa, hermes-* repos, gh CLI. Skills Hub: hermes-agent.nousresearch.com/docs/skills/.
§
GoRides: /data/workspace/gorides/ — Phase 0 done (177 files, 6 .NET 8 projects, builds clean). Svelte+Capacitor frontend, WinSMS, Paystack, SignalR, Docker→Railway. Phases 1-6 need TDD. Skills: large-scale-delegation (new), TDD v1.2 (updated), winsms-integration (new). Key: break large builds into phase-sized SDK prompts.