# Frontend — Three-Tab Digest Page

`web/index.html` + `web/styles.css` + `web/app.js`. No framework, no
build step — this must be openable by just hosting the `web/` folder as
static files (GitHub Pages is the natural free option, since the data
already lives in the same repo).

## Behavior

- Three tabs: **Learn**, **Trending**, **LinkedIn Ideas** — filter
  `data/digests/latest.json` client-side by `tab`.
- Each card: headline + summary, collapsed by default. Click/tap expands
  to show `why_it_matters` and a link to `source_url`.
- Cards with `colab_runnable: true` get a small badge (e.g. "🧪 Try on
  Colab") — purely visual, no extra logic needed beyond checking the flag.
- Show the digest's `date` somewhere visible (e.g. header: "As of
  2026-09-17") so it's obvious if the pipeline didn't run.
- Empty tab (0 cards that day) should show a plain "Nothing new today" —
  never a blank white section.

## Fetching the data

`app.js` does a plain `fetch('data/digests/latest.json')` relative to the
page — no API layer needed for v1 since everything is static JSON
committed by the Actions workflow.

## Styling

Keep it InShorts-like: card-based, generous whitespace, one clear visual
hierarchy (headline > summary > metadata). Dark-mode friendly is a nice
to have, not a requirement for the prototype.

## Prototype vs. real data

For the first prototype, hardcode a `data/digests/sample.json` with ~6
cards per tab covering realistic examples (e.g. a vLLM release note, a
PagedAttention explainer, a speculative decoding paper) so the UI can be
reviewed before the live pipeline is wired in. Point `app.js` at
`sample.json` initially; switching it to `latest.json` later is a
one-line change.
