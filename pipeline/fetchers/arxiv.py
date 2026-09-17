"""Fetcher for arXiv preprints."""

import datetime
from typing import List
import feedparser
import requests
import yaml
from pipeline.schema import RawItem


def fetch(config_path: str = "config/sources.yaml") -> List[RawItem]:
    """Fetch recent preprints from arXiv API for specified categories."""
    raw_items: List[RawItem] = []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            sources_cfg = yaml.safe_load(f) or {}
        arxiv_cfg = sources_cfg.get("arxiv", {})
    except Exception as e:
        print(f"[arXiv Fetcher Error] Could not load sources config: {e}")
        return []

    base_url = arxiv_cfg.get("base_url", "https://export.arxiv.org/api/query")
    categories = arxiv_cfg.get("categories", ["cs.LG", "cs.DC"])
    max_results = arxiv_cfg.get("max_results", 30)

    # Construct search query with + for arXiv OR queries
    cat_query = "+OR+".join([f"cat:{cat}" for cat in categories])
    query_url = (
        f"{base_url}?search_query={cat_query}"
        f"&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    )

    headers = {"User-Agent": "InferDaily/1.0"}

    try:
        response = requests.get(query_url, headers=headers, timeout=15)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            for entry in feed.entries:
                title = entry.get("title", "").replace("\n", " ").strip()
                summary = entry.get("summary", "").replace("\n", " ").strip()
                url = entry.get("link", "")
                published = entry.get("published", datetime.datetime.now(datetime.timezone.utc).isoformat())

                if title and url:
                    raw_items.append(
                        RawItem(
                            title=title,
                            raw_text=summary,
                            url=url,
                            source_name="arXiv",
                            published_at=published,
                        )
                    )
        else:
            print(f"[arXiv Fetcher Error] API returned status {response.status_code}")
    except Exception as e:
        print(f"[arXiv Fetcher Error] Failed fetching/parsing arXiv feed: {e}")

    return raw_items
