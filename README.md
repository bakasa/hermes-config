# hermes-config

Hermes Agent (OWL) configuration, skills, memories, and operational files.

## Contents

| Directory/File | Description |
|---|---|
| `skills/` | Hermes Agent skills (task-specific workflows) |
| `memories/` | Persistent memory entries across sessions |
| `cron/` | Scheduled cron jobs |
| `config.yaml` | Main Hermes Agent configuration |
| `SOUL.md` | Agent personality and behavioral guidelines |
| `auth.json` | Authentication configuration |
| `channel_directory.json` | Connected channel registry |

## Skills Included

- **autonomous-ai-agents** — Claude Code, Codex, OpenCode delegation
- **creative** — ASCII art, diagrams, image generation, video
- **data-science** — Jupyter notebooks, data analysis
- **devops** — Deployment orchestration, kanban, webhooks
- **email** — Himalaya IMAP/SMTP
- **gaming** — Minecraft, Pokemon
- **github** — PR workflow, code review, issues
- **media** — YouTube, Spotify, GIF search
- **mlops** — Model training, evaluation, inference
- **note-taking** — Obsidian vault
- **perp-trading-automation** — Trading bot automation
- **productivity** — Notion, Airtable, Google Workspace
- **red-teaming** — LLM jailbreak techniques
- **research** — arXiv, blog monitoring
- **smart-home** — Philips Hue
- **social-media** — X/Twitter
- **software-development** — Debugging, testing, planning
- **yuanbao** — Yuanbao groups

## Setup

```bash
# Clone into ~/.hermes/
cp -r skills ~/.hermes/
cp -r memories ~/.hermes/
cp config.yaml ~/.hermes/
cp SOUL.md ~/.hermes/
```

## Agent: OWL

Hermes Agent configured as a multi-model inference router + Slack gateway.
