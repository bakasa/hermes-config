---
name: research-agent
description: >
  Daily AI research agent. Scans news, blogs, arXiv, and market signals.
  Produces a structured digest of the most relevant developments.
  Runs as a scheduled cron job. Output feeds into the Subconscious agent
  for idea generation.
trigger_keywords:
  - research scan
  - daily digest
  - ai news
  - what's new
  - scan feeds
---

# Research Agent

Scans the AI landscape daily and produces a structured digest of signals, news, and developments.

## Sources

### AI News & Blogs (via blogwatcher-cli)
- Import from OPML or add individual feeds
- Key sources to track (see `references/feed-list.md`)

### Academic Papers (via arXiv skill)
- Search: `cs.AI`, `cs.LG`, `cs.CL`, `cs.CV`
- Filter by relevance and citation velocity

### Market Signals (via Polymarket skill)
- AI-related prediction markets
- Funding and M&A activity signals

### Social Signals (via x_search / web_search)
- X/Twitter trending in AI circles
- Hacker News top posts
- Reddit r/MachineLearning, r/LocalLLaMA

## Output Format

Save digest to `~/.hermes/research/digests/YYYY-MM-DD.md`:

```markdown
# Research Digest — YYYY-MM-DD

## 🔥 Top Signals
[3-5 most important developments]

## 📰 AI News
[News articles, blog posts, announcements]

## 📄 Papers
[Notable arXiv papers with links]

## 📊 Market Signals
[Polymarket movements, funding news]

## 💡 Ideas for Subconscious
[Raw signals formatted as potential build ideas]
```

## Workflow

1. **Scan feeds** — `blogwatcher-cli scan` for new articles
2. **Search arXiv** — recent papers in AI/ML categories
3. **Check markets** — Polymarket AI markets
4. **Social scan** — X/Twitter, HN, Reddit for trending topics
5. **Synthesize** — combine into structured digest
6. **Save** — write to `~/.hermes/research/digests/YYYY-MM-DD.md`
7. **Report** — deliver summary to Main agent via Slack

## Cron Schedule

- **Daily at 06:00 UTC** — full scan + digest
- **Weekly on Monday** — extended analysis + trend report

## References

- `references/feed-list.md` — curated list of AI blogs and news sources
- `references/search-queries.md` — arXiv and web search query templates
