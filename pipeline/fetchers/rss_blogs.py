"""Fetcher for RSS/Atom engineering blogs."""

import datetime
from typing import List, Dict, Any
import feedparser
import yaml
from pipeline.schema import RawItem


def fetch(config_path: str = "config/sources.yaml") -> List[RawItem]:
    """Fetch blog posts from RSS feeds configured in sources.yaml."""
    raw_items: List[RawItem] = []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            sources_cfg = yaml.safe_load(f) or {}
        blogs = sources_cfg.get("rss_blogs", [])
    except Exception as e:
        print(f"[RSS Fetcher Error] Could not load sources config: {e}")
        return []

    for blog in blogs:
        blog_name = blog.get("name", "Blog")
        feed_url = blog.get("url")
        if not feed_url:
            continue

        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # Up to top 10 per blog
                title = entry.get("title", "").replace("\n", " ").strip()
                summary_raw = (
                    entry.get("summary") or entry.get("description") or ""
                )
                import re
                summary_clean = re.sub(r"<[^>]+>", "", summary_raw).replace("\n", " ").strip()
                url = entry.get("link", "")
                
                # Parse published date
                published = entry.get("published") or entry.get("updated") or ""
                if not published:
                    published = datetime.datetime.now(datetime.timezone.utc).isoformat()

                if title and url:
                    raw_items.append(
                        RawItem(
                            title=title,
                            raw_text=summary_clean,
                            url=url,
                            source_name=blog_name,
                            published_at=published,
                        )
                    )
        except Exception as e:
            print(f"[RSS Fetcher Error] Failed fetching RSS feed for {blog_name}: {e}")

    return raw_items
