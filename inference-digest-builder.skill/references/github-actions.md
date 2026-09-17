# GitHub Actions — Daily Cron

`.github/workflows/daily-digest.yml` runs the pipeline daily and commits
the result, so the static frontend always has fresh data with zero
external hosting for the backend.

## Workflow shape

```yaml
name: Daily Digest
on:
  schedule:
    - cron: "30 0 * * *"   # ~6:00 AM IST (00:30 UTC) — adjust as needed
  workflow_dispatch: {}     # allow manual runs from the Actions tab

jobs:
  build-digest:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python -m pipeline.run_digest
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit updated digest
        run: |
          git config user.name "digest-bot"
          git config user.email "actions@github.com"
          git add data/digests/
          git commit -m "Daily digest: $(date -u +%Y-%m-%d)" || echo "No changes"
          git push
```

## Notes

- `workflow_dispatch` is included so a run can be triggered manually to
  test without waiting for the schedule.
- `secrets.GITHUB_TOKEN` is provided automatically by Actions — no setup
  needed for the GitHub fetcher's auth.
- Whichever LLM API key `summarize.py` needs goes in repo Secrets
  (Settings → Secrets and variables → Actions) — never committed.
- The `git commit ... || echo "No changes"` guard prevents the job from
  failing on days where, for some reason, nothing changed.
- If the frontend is hosted via GitHub Pages from the same repo, enable
  Pages on the `main` branch, `/web` (or root, if `web/` contents are
  moved to the repo root — folder-structure.md keeps them separate, so
  configure Pages to serve `/web` as the site root, or add a small
  redirect at repo root — decide this only once the repo actually exists
  and Pages is being configured).
