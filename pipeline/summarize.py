"""LLM summarizer and tagger module."""

import datetime
import json
import os
import re
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from pipeline.schema import Card, RawItem, generate_card_id

# Load environment variables from .env file if present
load_dotenv()

SUMMARIZE_PROMPT_TEMPLATE = """You are an expert LLM/SLM inference engineer and technical editor.
Your task is to analyze the following raw news item and summarize it into a structured JSON card for "Infer/Daily".

Raw Item Title: {title}
Source: {source_name}
Raw Text Content:
{raw_text}

Respond ONLY with a valid JSON object (no markdown codeblock formatting, no extra text) matching this EXACT schema:
{{
  "tab": "learn" | "trending" | "linkedin_idea",
  "headline": "<Short, punchy title suitable for an InShorts card>",
  "summary": "<InShorts-style concise summary of 40-50 words max focusing on technical core>",
  "why_it_matters": "<One sentence framing why this matters to an inference engineer, e.g., latency, throughput, memory reduction>",
  "colab_runnable": true or false
}}

Classification Guidance:
- "learn": Foundational/explainer material or architectural insights (e.g., how KV cache works, FlashAttention explanations, continuous batching).
- "trending": Fresh news, new repository release (e.g. vLLM/SGLang release), benchmark report, or paper.
- "linkedin_idea": Unique, under-explained, contrarian, or high-discussion technical topic ideal for a LinkedIn breakdown.

Colab-Runnable Guidance:
- Set "colab_runnable" to true IF AND ONLY IF the text mentions small/quantized models (Qwen, Phi, Gemma, SmolLM, TinyLlama, GGUF, AWQ, GPTQ), bitsandbytes, Unsloth, consumer/T4 GPUs, or a Jupyter/Colab notebook link. Otherwise set false.
"""


def _call_llm_api(prompt: str) -> Optional[str]:
    """Call available LLM provider (NVIDIA NIM, OpenAI, or Anthropic)."""
    # 1. Try NVIDIA NIM (OpenAI compatible)
    nvidia_key = os.getenv("NVIDIA_NIM_API_KEY")
    if nvidia_key:
        nim_models = [
            "deepseek-ai/deepseek-v4-flash-0731",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "meta/llama-3.1-8b-instruct",
        ]
        for model in nim_models:
            try:
                from openai import OpenAI
                client = OpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=nvidia_key
                )
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=600,
                )
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
            except Exception as e:
                print(f"[LLM Warning] NVIDIA NIM model {model} failed: {e}")

    # 2. Try OpenAI API
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM Warning] OpenAI API call failed: {e}")

    # 3. Try Anthropic API
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import requests
            headers = {
                "x-api-key": anthropic_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt}],
            }
            resp = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=15)
            if resp.status_code == 200:
                res_data = resp.json()
                return res_data["content"][0]["text"]
        except Exception as e:
            print(f"[LLM Warning] Anthropic API call failed: {e}")

    return None


def _clean_json_response(raw_resp: str) -> str:
    """Strip markdown backticks if the model wraps JSON in ```json ... ```."""
    cleaned = raw_resp.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _fallback_summarize(item: RawItem, digest_date: str) -> Card:
    """Generate a fallback Card when LLM API is unavailable or fails."""
    title_lower = item.title.lower()
    text_lower = item.raw_text.lower()
    
    # Determine tab heuristic
    if "release" in title_lower or "pr #" in title_lower or "vllm" in title_lower:
        tab = "trending"
    elif "how" in title_lower or "guide" in title_lower or "understanding" in title_lower or "attention" in title_lower:
        tab = "learn"
    else:
        tab = "linkedin_idea"

    # Determine colab runnable heuristic
    colab_keywords = ["qwen", "phi", "gemma", "smollm", "tinyllama", "gguf", "awq", "gptq", "bitsandbytes", "unsloth", "colab", "t4"]
    colab_runnable = any(kw in title_lower or kw in text_lower for kw in colab_keywords)

    # Word-trimmed summary without HTML tags
    clean_raw = re.sub(r"<[^>]+>", "", item.raw_text)
    words = clean_raw.split()
    summary_words = words[:45] if len(words) > 45 else words
    summary_text = " ".join(summary_words) if summary_words else item.title

    return Card(
        id=generate_card_id(item.url),
        tab=tab,
        headline=item.title[:75],
        summary=summary_text,
        why_it_matters=f"Key development in {item.source_name} impacting inference serving performance and workflow optimization.",
        colab_runnable=colab_runnable,
        source_name=item.source_name,
        source_url=item.url,
        date=digest_date,
    )


def summarize_item(item: RawItem, digest_date: str) -> Optional[Card]:
    """Turn a RawItem into a tagged Card via LLM call with 1 retry on parse failure."""
    prompt = SUMMARIZE_PROMPT_TEMPLATE.format(
        title=item.title,
        source_name=item.source_name,
        raw_text=item.raw_text[:2000]  # truncate long text
    )

    for attempt in range(2):
        raw_resp = _call_llm_api(prompt)
        if not raw_resp:
            # Fallback if no LLM key available
            return _fallback_summarize(item, digest_date)

        try:
            cleaned_json = _clean_json_response(raw_resp)
            data = json.loads(cleaned_json)
            
            tab = data.get("tab")
            if tab not in ("learn", "trending", "linkedin_idea"):
                tab = "trending"

            return Card(
                id=generate_card_id(item.url),
                tab=tab,
                headline=str(data.get("headline", item.title[:75])),
                summary=str(data.get("summary", item.raw_text[:200])),
                why_it_matters=str(data.get("why_it_matters", "")),
                colab_runnable=bool(data.get("colab_runnable", False)),
                source_name=item.source_name,
                source_url=item.url,
                date=digest_date,
            )
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"[Summarize Parse Error] Attempt {attempt+1} failed for {item.title}: {e}")
            if attempt == 1:
                # Fallback after 2 failed attempts
                return _fallback_summarize(item, digest_date)

    return _fallback_summarize(item, digest_date)
