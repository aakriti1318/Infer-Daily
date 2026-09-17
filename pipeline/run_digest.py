"""Main pipeline orchestrator: fetch -> filter -> summarize -> cap -> write JSON."""

import datetime
import json
import os
import shutil
from typing import List, Dict, Any

from pipeline.schema import Card, RawItem
from pipeline.filter import filter_raw_items
from pipeline.summarize import summarize_item
from pipeline.fetchers import arxiv, github_releases, rss_blogs, hackernews


def run_pipeline():
    """Run the complete news digest pipeline."""
    today_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    print(f"=== Starting Infer/Daily Digest Run for {today_str} ===")

    # 1. Execute Fetchers (Fail-Soft per fetcher)
    all_raw_items: List[RawItem] = []
    source_stats: Dict[str, str] = {}

    fetchers = [
        ("arXiv", arxiv.fetch),
        ("GitHub", github_releases.fetch),
        ("RSS Blogs", rss_blogs.fetch),
        ("Hacker News", hackernews.fetch),
    ]

    for name, fetch_fn in fetchers:
        try:
            print(f"[*] Fetching from {name}...")
            items = fetch_fn()
            all_raw_items.extend(items)
            source_stats[name] = f"SUCCESS ({len(items)} raw items)"
            print(f"    -> Retrieved {len(items)} raw items from {name}")
        except Exception as e:
            source_stats[name] = f"FAILED ({e})"
            print(f"[!] Error fetching from {name}: {e}")

    print("\n--- Fetch Summary ---")
    for src, status in source_stats.items():
        print(f"  {src}: {status}")

    print(f"\nTotal raw items collected: {len(all_raw_items)}")

    # 2. Filter Items by Keyword Relevance
    filtered_items = filter_raw_items(all_raw_items)
    print(f"Items after keyword filtering & deduplication: {len(filtered_items)}")

    # 3. Summarize & Tag Cards Concurrently
    cards_by_tab: Dict[str, List[Card]] = {
        "learn": [],
        "trending": [],
        "linkedin_idea": [],
    }

    print("\n[*] Summarizing items concurrently with LLM / fallback...")
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_single(item):
        return summarize_item(item, today_str)

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_item = {executor.submit(process_single, item): item for item in filtered_items}
        for future in as_completed(future_to_item):
            item = future_to_item[future]
            try:
                card = future.result()
                if card and card.tab in cards_by_tab:
                    cards_by_tab[card.tab].append(card)
                    print(f"  [✓] Tagged '{card.headline[:45]}' -> {card.tab}")
            except Exception as e:
                print(f"  [!] Error summarizing {item.title[:40]}: {e}")

    # 4. Cap at 6 cards per tab
    final_cards: List[Card] = []
    print("\n--- Card Counts Before Cap ---")
    for tab_name, tab_cards in cards_by_tab.items():
        print(f"  {tab_name}: {len(tab_cards)} cards")
        # Cap at 6 cards max per tab
        capped_cards = tab_cards[:6]
        final_cards.extend(capped_cards)

    print(f"\nFinal total cards in digest: {len(final_cards)}")

    # 5. Write JSON outputs
    os.makedirs("data/digests", exist_ok=True)
    os.makedirs("web/data/digests", exist_ok=True)
    
    dated_file = f"data/digests/{today_str}.json"
    latest_file = "data/digests/latest.json"
    web_latest_file = "web/latest.json"
    web_digests_file = "web/data/digests/latest.json"

    cards_json = [card.to_dict() for card in final_cards]

    with open(dated_file, "w", encoding="utf-8") as f:
        json.dump(cards_json, f, indent=2, ensure_ascii=False)
    print(f"[✓] Wrote dated digest to {dated_file}")

    shutil.copyfile(dated_file, latest_file)
    shutil.copyfile(dated_file, web_latest_file)
    shutil.copyfile(dated_file, web_digests_file)
    print(f"[✓] Updated latest digest copies in data/ and web/")

    print("=== Infer/Daily Digest Pipeline Finished Successfully ===")


if __name__ == "__main__":
    run_pipeline()
