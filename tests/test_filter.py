"""Unit tests for keyword filter logic."""

import json
from pipeline.schema import RawItem
from pipeline.filter import filter_raw_items, is_relevant_item


def test_is_relevant_item():
    item_relevant = RawItem(
        title="vLLM v0.6.2 Released",
        raw_text="Multi-step execution support for serving.",
        url="https://example.com/vllm",
        source_name="GitHub",
        published_at="2026-09-17T00:00:00Z"
    )

    item_irrelevant = RawItem(
        title="Random Cooking Recipe",
        raw_text="How to bake sourdough bread",
        url="https://example.com/bread",
        source_name="Blog",
        published_at="2026-09-17T00:00:00Z"
    )

    keywords = {"vllm", "speculative decoding", "pagedattention"}
    assert is_relevant_item(item_relevant, keywords) is True
    assert is_relevant_item(item_irrelevant, keywords) is False


def test_filter_raw_items():
    with open("tests/fixtures/sample_raw_items.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_items = [RawItem.from_dict(d) for d in data]
    filtered = filter_raw_items(raw_items, config_path="config/keywords.yaml")

    # Should keep vLLM and Speculative Decoding items, exclude bread recipe
    assert len(filtered) == 2
    urls = [item.url for item in filtered]
    assert "https://github.com/vllm-project/vllm/releases/tag/v0.6.2" in urls
    assert "https://arxiv.org/abs/2211.17192" in urls
    assert "https://example.com/blog/bread-recipe" not in urls
