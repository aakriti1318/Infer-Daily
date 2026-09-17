"""Fetcher for Hacker News submissions via Algolia API."""

import datetime
from typing import List, Set
import requests
import yaml
from pipeline.schema import RawItem
from pipeline.filter import load_keywords


def fetch(config_path: str = "config/sources.yaml", keywords_path: str = "config/keywords.yaml") -> List[RawItem]:
    """Fetch recent HN submissions matching keywords from Algolia API."""
    raw_items: List[RawItem] = []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            sources_cfg = yaml.safe_load(f) or {}
        hn_cfg = sources_cfg.get("hackernews", {})
    except Exception as e:
        print(f"[HN Fetcher Error] Could not load sources config: {e}")
        return []

    base_url = hn_cfg.get("base_url", "https://hn.algolia.com/api/v1/search_by_date")
    
    # Pick key search queries to query Algolia API
    queries = ["vllm", "sglang", "tensorrt-llm", "pagedattention", "speculative decoding", "llm inference", "slm benchmark"]

    # Restrict to last 48 hours
    two_days_ago = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)).timestamp())
    numeric_filters = f"created_at_i>{two_days_ago}"

    for query in queries:
        try:
            params = {
                "query": query,
                "tags": "story",
                "numericFilters": numeric_filters,
                "hitsPerPage": 10,
            }
            resp = requests.get(base_url, params=params, timeout=10)
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                for hit in hits:
                    title = hit.get("title", "").strip()
                    url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
                    story_text = hit.get("story_text") or ""
                    created_at = hit.get("created_at") or ""
                    
                    if title and url:
                        raw_items.append(
                            RawItem(
                                title=title,
                                raw_text=story_text or title,
                                url=url,
                                source_name="Hacker News",
                                published_at=created_at,
                            )
                        )
        except Exception as e:
            print(f"[HN Fetcher Error] Failed fetching HN query '{query}': {e}")

    return raw_items
