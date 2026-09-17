---
name: inference-digest-builder
description: Build "Infer/Daily" — a personal daily InShorts-style digest web app for LLM/SLM inference-engineering news (vLLM, SGLang, TensorRT-LLM, llm-d, benchmarking). Use this skill whenever the user asks to build, extend, or fix the digest app, its fetch/summarize pipeline, its GitHub Actions cron job, or its three-tab (Learn / Trending / LinkedIn Ideas) frontend. Always consult this skill before writing any code for this project, even for a small tweak, so folder structure and conventions stay consistent.
---

# Infer/Daily — Digest App Builder

Personal tool: every morning, pull inference-engineering news (papers, GitHub
releases, vendor blogs, HN) into three tabs — **Learn**, **Trending**,
**LinkedIn Ideas** — each capped at 6 InShorts-style cards (~50-word summary,
tap to expand). Runs on a free GitHub Actions cron; frontend is a static page
that reads generated JSON. No database required for v1.

## Before writing any code

1. Read `references/folder-structure.md` — the repo layout is fixed. Do not
   invent a different layout or scatter files at the repo root.
2. Read the reference file for whichever part you're touching (fetch,
   summarize, frontend, workflow, README) — each has its own conventions,
   schemas, and gotchas. Don't guess a JSON shape; it's specified there.
3. If touching more than one part, read all the relevant references first,
   then write code — the schemas have to agree across fetch → summarize →
   frontend.

## Build order (for a fresh build)

1. `references/folder-structure.md` — scaffold the repo.
2. `references/fetch-pipeline.md` — one fetcher module per source type.
3. `references/summarize-tag.md` — the LLM call that turns raw items into
   tagged cards; defines the canonical card JSON schema everything else
   depends on.
4. `references/frontend.md` — the static three-tab page that reads the card
   JSON.
5. `references/github-actions.md` — wires fetch → summarize into a daily
   cron, committing the output the frontend reads.
6. `references/readme-template.md` — fill in and place at repo root last,
   once the actual scripts/commands exist to document accurately.

## Core conventions (apply everywhere)

- **Language**: Python 3.11+ for all pipeline code (fetch, filter,
  summarize). Vanilla HTML/CSS/JS for the frontend — no framework, no build
  step, so it's trivial to host as a static page.
- **One responsibility per file.** A fetcher fetches. A filter filters. The
  summarizer only calls the LLM and validates its output. Never combine
  fetch+summarize in one script — it makes the pipeline impossible to
  re-run partially when one source breaks.
- **Fail soft per source.** If one fetcher (e.g. the GitHub API) errors or
  rate-limits, log it and continue with the other sources — never let one
  bad source kill the whole day's digest.
- **Config, not hardcoding.** Keyword lists, source URLs, and card caps
  live in `config/keywords.yaml` and `config/sources.yaml` — never inline
  in scripts. This is the file the user will edit most often.
- **Deterministic card schema.** Every card, regardless of source, is
  normalized to the schema in `references/summarize-tag.md` before it
  touches the frontend. The frontend must never need to know which source
  a card came from to render it.
- **No secrets in code.** API keys (if any source needs one) come from
  environment variables / GitHub Actions secrets, never hardcoded, never
  committed.
- **Comments explain *why*, not *what*.** Code should be minimal and
  readable; reserve comments for non-obvious decisions (e.g. "why we cap
  at 6 cards," "why this source is polled last").

## Keyword focus (seed config — user will extend this over time)

Inference/serving: inference, serving, vLLM, SGLang, TensorRT-LLM, llm-d,
PagedAttention, speculative decoding, KV cache, quantization, continuous
batching, disaggregated prefill/decode, FlashAttention, FlashInfer,
RadixAttention, chunked prefill, prefix caching, Medusa, EAGLE, lookahead
decoding, AWQ, GPTQ, GGUF, SmoothQuant, FP8, INT4, TGI, Triton Inference
Server, LMDeploy, MLC-LLM, llama.cpp, Ollama, Ray Serve, tensor
parallelism, pipeline parallelism, expert parallelism, outlines, xgrammar.

Benchmarking: LLM benchmark, SLM benchmark, GPU benchmark, CPU inference
benchmark, throughput, latency, tokens/sec, TTFT, TPOT, ITL, goodput,
MLPerf, capability benchmark, eval harness, genai-perf, guidellm.

Colab-runnable signal (see `references/summarize-tag.md` for how this
becomes a badge, not a tab): small/quantized models (Qwen, Phi, Gemma,
SmolLM, TinyLlama), bitsandbytes 4-bit, Unsloth, T4/free-tier GPU mentions,
linked notebooks.

## Definition of done for the prototype

- Sample/mock card data (matching the real schema) renders correctly in
  all three tabs with the Colab-runnable badge working.
- At least one real fetcher (start with arXiv — simplest API, no auth)
  runs end-to-end into real cards.
- The GitHub Actions workflow file is written and would run the pipeline
  on schedule, even if not yet enabled in a live repo.
- README accurately describes what actually exists — not the full vision.
