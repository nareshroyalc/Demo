"""Gemini embeddings. Returns None-safe results so the app still works (keyword-only) without a key."""
from __future__ import annotations

import time

from . import config

_client = None


def available() -> bool:
    return bool(config.GEMINI_API_KEY)


def client():
    global _client
    if _client is None:
        from google import genai

        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    from google.genai import types

    out: list[list[float]] = []
    for i in range(0, len(texts), 50):  # modest batches keep us under free-tier limits
        batch = texts[i : i + 50]
        for attempt in range(5):
            try:
                res = client().models.embed_content(
                    model=config.EMBED_MODEL,
                    contents=batch,
                    config=types.EmbedContentConfig(
                        task_type=task_type, output_dimensionality=config.EMBED_DIM
                    ),
                )
                out.extend(_normalize(e.values) for e in res.embeddings)
                break
            except Exception as exc:  # rate limit / transient
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt * 2)
    return out


def _normalize(v: list[float]) -> list[float]:
    # Reduced-dimension Gemini embeddings are not unit length; normalise for cosine.
    n = sum(x * x for x in v) ** 0.5 or 1.0
    return [x / n for x in v]


def embed_documents(texts: list[str]) -> list[list[float]]:
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    return _embed([text], "RETRIEVAL_QUERY")[0]
