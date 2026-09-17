# README Template

Fill this in and place at the repo root as `README.md` once the actual
scripts/commands exist — don't describe features that aren't built yet.

```markdown
# Infer/Daily

A personal daily digest of LLM/SLM inference-engineering news — vLLM,
SGLang, TensorRT-LLM, llm-d, benchmarking, and related research — served
as a three-tab, InShorts-style page: **Learn**, **Trending**, **LinkedIn
Ideas**.

## Why

Built to avoid cross-platform scrolling for inference-engineering news,
and to surface both fresh developments and evergreen explainers worth
writing about.

## How it works

1. A GitHub Actions cron job runs daily, fetching from arXiv, GitHub
   releases, vendor engineering blogs, and Hacker News.
2. Items are filtered by keyword relevance (see `config/keywords.yaml`),
   then summarized and tagged into one of three tabs by an LLM call.
3. Results are written to `data/digests/` and committed.
4. The static page in `web/` reads the latest digest and renders it.

## Repo layout

(Copy the tree from `folder-structure.md`, trimmed to what actually
exists at time of writing.)

## Running it locally

\`\`\`bash
pip install -r requirements.txt
python -m pipeline.run_digest
\`\`\`

Requires an `ANTHROPIC_API_KEY` (or whichever LLM API is used) in your
environment.

## Configuration

- `config/keywords.yaml` — edit to add/remove topics tracked.
- `config/sources.yaml` — edit to add/remove feeds and API endpoints.

## Status

(Be honest here — e.g. "arXiv + GitHub fetchers live; RSS and HN fetchers
in progress. Frontend renders sample data; live wiring pending.")
```
