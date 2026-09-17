# Fetch Pipeline

Each fetcher in `pipeline/fetchers/` is a standalone module with one
function: `fetch() -> list[RawItem]`. No fetcher calls another. No fetcher
calls the LLM. No fetcher filters — that's `filter.py`'s job.

## RawItem shape (pre-summarization, pre-tagging)

```python
{
  "title": str,
  "raw_text": str,        # abstract, blog excerpt, PR description, HN text — whatever's available
  "url": str,
  "source_name": str,     # "arXiv", "GitHub: vllm-project/vllm", "NVIDIA Blog", "Hacker News"
  "published_at": str,    # ISO 8601
}
```

## Per-fetcher notes

- **arxiv.py** — Use the arXiv API (`http://export.arxiv.org/api/query`),
  category filters `cs.LG` + `cs.DC`, sorted by submission date, last
  24–48h. No auth needed. Start here — it's the simplest fetcher and a
  good first end-to-end test.
- **github_releases.py** — GitHub REST API, unauthenticated is fine for
  low volume but rate-limited to 60 req/hr; if that's tight, add a
  `GITHUB_TOKEN` env var (works as a GitHub Actions secret automatically —
  `secrets.GITHUB_TOKEN` is provided free in every Actions run). Pull
  releases *and* notable merged PRs for: `vllm-project/vllm`,
  `sgl-project/sglang`, `NVIDIA/TensorRT-LLM`, `llm-d/llm-d`.
- **rss_blogs.py** — Use `feedparser` against RSS/Atom feeds for NVIDIA
  Developer Blog, Red Hat AI blog, Anyscale/Ray blog, Baseten, Modal. One
  feed URL per source in `config/sources.yaml`, loop over them generically
  rather than one function per blog.
- **hackernews.py** — HN Algolia Search API
  (`https://hn.algolia.com/api/v1/search_by_date`), query by keyword,
  restrict to last 24–48h via `numericFilters=created_at_i>...`.

## Fail-soft requirement

`run_digest.py` calls each fetcher inside a try/except and logs+skips on
failure — one dead source must never take down the whole run. Log which
sources succeeded/failed at the end of each run so failures are visible
without digging through Actions logs.

## Filter (`filter.py`)

Input: all `RawItem`s from every fetcher, concatenated.
Output: the subset whose `title + raw_text` matches at least one keyword
from `config/keywords.yaml` (case-insensitive substring match is fine for
v1 — no need for embeddings yet). This runs *before* summarization so LLM
calls are only spent on relevant items.
