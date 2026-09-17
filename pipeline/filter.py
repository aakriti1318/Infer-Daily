"""Keyword relevance filter for RawItems."""

from typing import List, Set, Dict, Any
import yaml
from pipeline.schema import RawItem


def load_keywords(config_path: str = "config/keywords.yaml") -> Set[str]:
    """Load and flatten all keywords from keywords.yaml into lower-case set."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}
        
        keywords: Set[str] = set()
        for category, kw_list in data.items():
            if isinstance(kw_list, list):
                for kw in kw_list:
                    if isinstance(kw, str) and kw.strip():
                        keywords.add(kw.strip().lower())
        return keywords
    except Exception as e:
        print(f"[Warning] Failed to load keywords from {config_path}: {e}")
        return set()


def is_relevant_item(item: RawItem, keywords: Set[str]) -> bool:
    """Return True if item title or raw_text contains at least one keyword."""
    if not keywords:
        return True  # If no keywords loaded, pass items through
        
    combined_text = f"{item.title} {item.raw_text}".lower()
    for kw in keywords:
        if kw in combined_text:
            return True
    return False


def filter_raw_items(
    items: List[RawItem], config_path: str = "config/keywords.yaml"
) -> List[RawItem]:
    """Filter raw items based on keyword relevance and deduplicate by URL."""
    keywords = load_keywords(config_path)
    seen_urls: Set[str] = set()
    filtered: List[RawItem] = []

    for item in items:
        if not item.url or item.url in seen_urls:
            continue
        if is_relevant_item(item, keywords):
            seen_urls.add(item.url)
            filtered.append(item)

    return filtered
