# Summarize & Tag

`pipeline/summarize.py` takes filtered `RawItem`s and turns each into a
`Card` — the one schema the frontend and everything downstream relies on.
Defined once in `pipeline/schema.py`, imported everywhere else.

## Card schema (canonical — do not redefine elsewhere)

```python
{
  "id": str,                 # stable hash of url, for dedup across days
  "tab": "learn" | "trending" | "linkedin_idea",
  "headline": str,           # short, card-title length
  "summary": str,            # <= 50 words, InShorts style
  "why_it_matters": str,     # one line, inference-engineer framing
  "colab_runnable": bool,    # see badge logic below
  "source_name": str,
  "source_url": str,
  "date": str                # ISO 8601, date the digest was generated
}
```

## LLM prompt contract

One call per item. The prompt must instruct the model to return **only**
JSON matching the Card schema (minus `id`/`date`, which the script adds).
Always validate the response against the schema before writing it —
retry once on a parse failure, then drop the item and log it rather than
crashing the run.

Tagging guidance to put in the prompt:
- `learn` — foundational/explainer material, evergreen value regardless
  of publish date (e.g. "what is PagedAttention", a good writeup of how
  continuous batching works).
- `trending` — genuinely new/timely: a release, a benchmark result, a
  paper dropped in the last day or two.
- `linkedin_idea` — worth turning into a LinkedIn post; can overlap with
  either of the above. Bias toward items with an under-explained or
  contrarian angle, since the user already covers the popular topics.

## Colab-runnable badge

Not a tab — a boolean flag any card can carry. Set `colab_runnable: true`
when the raw text mentions any of: a small/quantized model name (Qwen,
Phi, Gemma, SmolLM, TinyLlama, or anything explicitly GGUF/AWQ/GPTQ
quantized), `bitsandbytes`, `Unsloth`, a free-tier/consumer GPU (T4,
Colab), or a linked notebook. Include this instruction directly in the
summarization prompt so it's decided in the same LLM call, rather than as
a second pass.

## Card cap

`run_digest.py` caps each tab at 6 cards after summarization — if more
than 6 qualify for a tab on a given day, keep the 6 most recent by
`published_at` from the raw item (don't ask the LLM to rank; that's an
extra unreliable call for marginal benefit at this scale).

## Output

`run_digest.py` writes `data/digests/YYYY-MM-DD.json` — an array of Cards
— and updates `data/digests/latest.json` to match (copy, not symlink, so
it survives a plain `git commit`).
