# Infer/Daily

A personal daily digest of LLM/SLM inference-engineering news — vLLM, SGLang, TensorRT-LLM, llm-d, benchmarking, and related research — served as a three-tab, InShorts-style web page: **Learn**, **Trending**, **LinkedIn Ideas**.

## Why

Built to eliminate cross-platform scrolling for inference-engineering news and to surface both fresh developments and evergreen explainers worth writing about.

## How It Works

1. A GitHub Actions cron job runs daily, fetching from arXiv, GitHub releases/PRs, vendor engineering blogs, and Hacker News.
2. Items are filtered by keyword relevance (`config/keywords.yaml`), then summarized and tagged into one of three tabs by an LLM call.
3. Results are written to `data/digests/` and committed automatically.
4. The static web page in `web/` reads the latest digest and renders interactive card feeds.

## Repo Layout

```
infer-daily/
├── README.md
├── .github/
│   └── workflows/
│       └── daily-digest.yml        # daily cron workflow
├── config/
│   ├── keywords.yaml                # editable keyword list
│   └── sources.yaml                 # source URLs and endpoints
├── pipeline/
│   ├── __init__.py
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── arxiv.py                 # arXiv API fetcher
│   │   ├── github_releases.py       # GitHub REST API fetcher
│   │   ├── rss_blogs.py             # RSS engineering blogs fetcher
│   │   └── hackernews.py            # HN Algolia API fetcher
│   ├── filter.py                    # keyword relevance filter
│   ├── summarize.py                 # LLM summarizer & tagger
│   ├── schema.py                    # Card & RawItem data schemas
│   └── run_digest.py                # pipeline orchestrator
├── data/
│   └── digests/
│       ├── latest.json              # copy of latest digest
│       └── YYYY-MM-DD.json          # daily digest files
├── web/
│   ├── index.html                   # static three-tab app
│   ├── styles.css                   # dark-mode glassmorphism styling
│   └── app.js                       # renders digest JSON cards
└── tests/
    ├── test_filter.py
    └── test_schema.py
```

## Running Locally

### Install dependencies

```bash
uv pip install -r requirements.txt
# or: pip install -r requirements.txt
```

### Run tests

```bash
uv run pytest
```

### Execute the digest pipeline

```bash
python -m pipeline.run_digest
```

Supported LLM provider keys in `.env` or system environment:
- `NVIDIA_NIM_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

If no key is present, the pipeline gracefully falls back to deterministic heuristic card generation for local testing.

## Configuration

- `config/keywords.yaml` — edit to add/remove topics tracked.
- `config/sources.yaml` — edit to add/remove RSS feeds and GitHub repos.

## Status

- **Pipeline**: Fully built with arXiv, GitHub, RSS blogs, and Hacker News fetchers.
- **LLM Summarizer**: Built with multi-provider support (NVIDIA NIM / OpenAI / Anthropic) and soft fallback.
- **Frontend**: Fully built static three-tab InShorts UI in `web/`.
- **Automation**: GitHub Actions daily cron workflow configured in `.github/workflows/daily-digest.yml`.
