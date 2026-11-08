"""Explicit Gemini prompt cache (with a TTL) for the stable part of every request.

What is cached: the persona's system prompt (rules + persona instructions + skills) and its tool declarations.
This prefix is identical on every request for a persona; the cache lets Gemini reuse it instead of reprocessing it.

Safety first: caching is an optimisation, never a dependency.
  * If the API refuses (endpoint unavailable on this key, prefix below the model's minimum size, quota ...),
    get() returns None and the agent sends the full prompt as before. After a failure we do not retry for
    RETRY_AFTER seconds, so a key without cache access costs at most one failed call per half hour.
  * The cache key includes a hash of the prompt + tools + model, so editing a skill or persona file creates a
    fresh cache instead of serving a stale one.
  * Caches are refreshed REFRESH_MARGIN seconds before their TTL ends; the old one is deleted (best effort).

PROMPT_CACHE=auto (default) tries it; PROMPT_CACHE=off disables it. PROMPT_CACHE_TTL_SECONDS sets the TTL.
Note: Gemini bills explicit-cache storage per hour of TTL on plans where it is available.
"""
from __future__ import annotations

import hashlib
import threading
import time

from . import config, embeddings

RETRY_AFTER = 1800  # seconds to wait after a failed attempt
REFRESH_MARGIN = 120  # re-create this long before the TTL runs out

_lock = threading.Lock()
_entries: dict[str, dict] = {}  # persona id -> {"name", "expires", "hash"}
_state = {"disabled_until": 0.0, "last_error": None, "attempts": 0, "created": 0, "hits": 0}


def enabled() -> bool:
    return config.PROMPT_CACHE != "off" and embeddings.available()


def _hash(system_prompt: str, tool) -> str:
    h = hashlib.sha256()
    for part in (config.CHAT_MODEL, system_prompt, tool.model_dump_json(exclude_none=True)):
        h.update(part.encode("utf-8"))
    return h.hexdigest()


def get(persona: dict, system_prompt: str, tool) -> str | None:
    """Return the cache name to send as `cached_content`, creating/refreshing it when needed; None = no cache."""
    if not enabled():
        return None
    pid, digest, now = persona["id"], _hash(system_prompt, tool), time.time()
    with _lock:
        entry = _entries.get(pid)
        if entry and entry["hash"] == digest and entry["expires"] - now > REFRESH_MARGIN:
            _state["hits"] += 1
            return entry["name"]
        if now < _state["disabled_until"]:
            return None
        _state["attempts"] += 1
        try:
            from google.genai import types

            client = embeddings.client()
            cache = client.caches.create(
                model=config.CHAT_MODEL,
                config=types.CreateCachedContentConfig(
                    system_instruction=system_prompt,
                    tools=[tool],
                    ttl=f"{config.PROMPT_CACHE_TTL_SECONDS}s",
                    display_name=f"brightline-{pid}",
                ),
            )
        except Exception as e:  # unavailable / too small / quota: fall back to the normal prompt
            _state["last_error"] = f"{type(e).__name__}: {str(e)[:160]}"
            _state["disabled_until"] = now + RETRY_AFTER
            return None
        old = _entries.get(pid)
        _entries[pid] = {"name": cache.name, "expires": now + config.PROMPT_CACHE_TTL_SECONDS, "hash": digest}
        _state["created"] += 1
        _state["last_error"] = None
        if old and old["name"] != cache.name:
            try:
                client.caches.delete(name=old["name"])
            except Exception:
                pass
        return cache.name


def invalidate(persona_id: str) -> None:
    """Forget a cache that a request just failed with (for example it was deleted or expired early)."""
    with _lock:
        _entries.pop(persona_id, None)


def status() -> dict:
    return {
        "mode": config.PROMPT_CACHE,
        "ttl_seconds": config.PROMPT_CACHE_TTL_SECONDS,
        "active": sorted(_entries),
        "create_attempts": _state["attempts"],
        "created": _state["created"],
        "reused": _state["hits"],
        "last_error": _state["last_error"],
        "retry_in_seconds": max(0, int(_state["disabled_until"] - time.time())),
    }
