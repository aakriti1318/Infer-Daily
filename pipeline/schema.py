"""Canonical schemas for RawItem and Card data objects."""

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Dict, Literal


@dataclass
class RawItem:
    title: str
    raw_text: str
    url: str
    source_name: str
    published_at: str  # ISO 8601 string

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RawItem":
        return cls(
            title=data.get("title", ""),
            raw_text=data.get("raw_text", ""),
            url=data.get("url", ""),
            source_name=data.get("source_name", ""),
            published_at=data.get("published_at", ""),
        )


def generate_card_id(url: str) -> str:
    """Generate a stable short hash ID from a source URL."""
    return hashlib.sha256(url.strip().encode("utf-8")).hexdigest()[:12]


@dataclass
class Card:
    id: str
    tab: Literal["learn", "trending", "linkedin_idea"]
    headline: str
    summary: str
    why_it_matters: str
    colab_runnable: bool
    source_name: str
    source_url: str
    date: str  # YYYY-MM-DD

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        return cls(
            id=data.get("id") or generate_card_id(data.get("source_url", "")),
            tab=data.get("tab", "trending"),
            headline=data.get("headline", ""),
            summary=data.get("summary", ""),
            why_it_matters=data.get("why_it_matters", ""),
            colab_runnable=bool(data.get("colab_runnable", False)),
            source_name=data.get("source_name", ""),
            source_url=data.get("source_url", ""),
            date=data.get("date", ""),
        )
