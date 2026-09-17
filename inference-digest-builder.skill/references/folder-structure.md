# Folder Structure

This layout is fixed. Every part of the skill assumes files live here —
don't rename or flatten it.

```
infer-daily/
├── README.md
├── .github/
│   └── workflows/
│       └── daily-digest.yml        # cron: fetch -> filter -> summarize -> commit
├── config/
│   ├── keywords.yaml                # editable keyword list, by category
│   └── sources.yaml                 # source URLs / API endpoints, per fetcher
├── pipeline/
│   ├── __init__.py
│   ├── fetchers/
│   │   ├── __init__.py
│   │   ├── arxiv.py
│   │   ├── github_releases.py
│   │   ├── rss_blogs.py             # NVIDIA, Red Hat, Anyscale, Baseten, Modal
│   │   └── hackernews.py
│   ├── filter.py                    # keyword/relevance filter, shared by all fetchers
│   ├── summarize.py                 # LLM call: raw item -> tagged card (see summarize-tag.md)
│   ├── schema.py                    # the Card dataclass/schema, single source of truth
│   └── run_digest.py                # orchestrator: calls fetchers -> filter -> summarize -> writes JSON
├── data/
│   └── digests/
│       └── YYYY-MM-DD.json          # one file per day, written by run_digest.py
├── web/
│   ├── index.html                   # the three-tab page
│   ├── styles.css
│   └── app.js                       # reads data/digests/latest.json (or dated file), renders cards
└── tests/
    ├── test_filter.py
    ├── test_schema.py
    └── fixtures/
        └── sample_raw_items.json    # for testing fetchers/filter without hitting live APIs
```

## Notes

- `data/digests/` is committed to the repo by the GitHub Actions workflow
  — this is what makes the static frontend work with no database. Keep a
  `latest.json` (symlink or copy of the most recent date) so `web/app.js`
  doesn't need to know today's date.
- `config/` is the only place non-technical edits should be needed —
  adding a keyword or a new RSS feed should never require touching
  `pipeline/`.
- `pipeline/schema.py` is imported by both `summarize.py` and any test —
  never redefine the card shape in more than one place.
- Keep `web/` framework-free and dependency-free so it can be published as
  a static page with zero build step.
