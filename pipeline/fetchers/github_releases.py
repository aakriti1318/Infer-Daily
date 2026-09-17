"""Fetcher for GitHub releases and recent pull requests from key inference repos."""

import os
from typing import List, Dict, Any
import requests
import yaml
from pipeline.schema import RawItem


def fetch(config_path: str = "config/sources.yaml") -> List[RawItem]:
    """Fetch releases and merged PRs for configured GitHub repositories."""
    raw_items: List[RawItem] = []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            sources_cfg = yaml.safe_load(f) or {}
        github_cfg = sources_cfg.get("github", {})
    except Exception as e:
        print(f"[GitHub Fetcher Error] Could not load sources config: {e}")
        return []

    repos = github_cfg.get("repos", [
        "vllm-project/vllm",
        "sgl-project/sglang",
        "NVIDIA/TensorRT-LLM",
        "llm-d/llm-d",
    ])
    max_releases = github_cfg.get("max_releases_per_repo", 5)
    max_prs = github_cfg.get("max_prs_per_repo", 5)

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "InferDaily-DigestApp",
    }
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    for repo in repos:
        # 1. Fetch Releases
        releases_url = f"https://api.github.com/repos/{repo}/releases?per_page={max_releases}"
        try:
            resp = requests.get(releases_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                releases = resp.json()
                for rel in releases:
                    tag_name = rel.get("tag_name", "")
                    title = f"[{repo}] Release {tag_name}: {rel.get('name') or tag_name}"
                    body = rel.get("body") or ""
                    url = rel.get("html_url") or f"https://github.com/{repo}/releases/tag/{tag_name}"
                    published_at = rel.get("published_at") or ""
                    if title and url:
                        raw_items.append(
                            RawItem(
                                title=title,
                                raw_text=body,
                                url=url,
                                source_name=f"GitHub: {repo}",
                                published_at=published_at,
                            )
                        )
            else:
                print(f"[GitHub Fetcher] Releases API returned status {resp.status_code} for {repo}")
        except Exception as e:
            print(f"[GitHub Fetcher Error] Failed fetching releases for {repo}: {e}")

        # 2. Fetch Merged PRs / Closed PRs
        prs_url = f"https://api.github.com/repos/{repo}/pulls?state=closed&sort=updated&direction=desc&per_page={max_prs}"
        try:
            resp = requests.get(prs_url, headers=headers, timeout=10)
            if resp.status_code == 200:
                prs = resp.json()
                for pr in prs:
                    if pr.get("merged_at"):  # Only merged PRs
                        pr_num = pr.get("number")
                        title = f"[{repo}] PR #{pr_num}: {pr.get('title') or ''}"
                        body = pr.get("body") or ""
                        url = pr.get("html_url") or ""
                        merged_at = pr.get("merged_at") or ""
                        if title and url:
                            raw_items.append(
                                RawItem(
                                    title=title,
                                    raw_text=body,
                                    url=url,
                                    source_name=f"GitHub: {repo}",
                                    published_at=merged_at,
                                )
                            )
        except Exception as e:
            print(f"[GitHub Fetcher Error] Failed fetching PRs for {repo}: {e}")

    return raw_items
