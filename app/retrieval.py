"""Shared retrieval layer used by BOTH /mcp (tools) and /agent (generation).

Docs:  hybrid search = Qdrant vector search + BM25 keyword search, merged with reciprocal-rank fusion.
DB:    schema introspection + a strictly read-only SQL runner.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
from typing import Any

from . import config, embeddings

_lock = threading.Lock()
_qdrant = None
_chunks: list[dict] | None = None
_bm25 = None


# ------------------------------------------------------------------ docs side
def get_qdrant():
    """Qdrant in embedded/local mode: files under data/qdrant, no server needed."""
    global _qdrant
    with _lock:
        if _qdrant is None:
            from qdrant_client import QdrantClient

            config.QDRANT_PATH.mkdir(parents=True, exist_ok=True)
            _qdrant = QdrantClient(path=str(config.QDRANT_PATH))
        return _qdrant


def reset_caches() -> None:
    global _chunks, _bm25
    _chunks, _bm25 = None, None


def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9$%]+", s.lower())


def _load_chunks() -> list[dict]:
    global _chunks, _bm25
    if _chunks is None:
        from rank_bm25 import BM25Okapi

        from .ingest import CHUNK_CACHE, parse_docs

        if CHUNK_CACHE.exists():
            _chunks = json.loads(CHUNK_CACHE.read_text(encoding="utf-8"))
        else:
            _chunks = parse_docs()
        _bm25 = BM25Okapi([_tok(c["text"]) for c in _chunks]) if _chunks else None
    return _chunks


def _vector_hits(query: str, k: int) -> list[dict]:
    if not embeddings.available():
        return []
    q = get_qdrant()
    if not q.collection_exists(config.COLLECTION):
        return []
    res = q.query_points(config.COLLECTION, query=embeddings.embed_query(query), limit=k, with_payload=True)
    return [{"id": str(p.id), **p.payload} for p in res.points]


def _keyword_hits(query: str, k: int) -> list[dict]:
    chunks = _load_chunks()
    if not chunks or _bm25 is None:
        return []
    scores = _bm25.get_scores(_tok(query))
    order = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)[:k]
    return [chunks[i] for i in order if scores[i] > 0]


def search_docs(query: str, k: int = 5, doc: str | None = None) -> list[dict]:
    """Hybrid search. Returns [{doc, title, page, text, score, ...}] best-first, with citations."""
    k = max(1, min(int(k), 10))
    pool = k * 4
    ranked: dict[str, dict] = {}
    for hits in (_vector_hits(query, pool), _keyword_hits(query, pool)):
        for rank, h in enumerate(hits):
            cur = ranked.setdefault(h["id"], {**h, "score": 0.0})
            cur["score"] += 1.0 / (60 + rank + 1)  # reciprocal-rank fusion
    results = sorted(ranked.values(), key=lambda r: r["score"], reverse=True)
    if doc:
        results = [r for r in results if doc.lower() in r["doc"].lower()]
    out = []
    for r in results[:k]:
        out.append(
            {
                "doc": r["doc"],
                "title": r["title"],
                "page": r["page"],
                "score": round(r["score"], 4),
                "text": r["text"],
                "citation": f"{r['title']} ({r['doc']}), p.{r['page']}",
            }
        )
    return out


def list_documents() -> list[dict]:
    docs: dict[str, dict] = {}
    for c in _load_chunks():
        d = docs.setdefault(c["doc"], {"doc": c["doc"], "title": c["title"], "pages": 0, "chunks": 0})
        d["pages"] = max(d["pages"], c["page"])
        d["chunks"] += 1
    return sorted(docs.values(), key=lambda d: d["doc"])


def get_document_page(doc: str, page: int) -> dict:
    parts = [c for c in _load_chunks() if c["doc"] == doc and c["page"] == page]
    if not parts:
        return {"error": f"No text for {doc} page {page}. Use list_documents() to see valid names/pages."}
    return {"doc": doc, "title": parts[0]["title"], "page": page, "text": "\n\n".join(p["text"] for p in parts)}


# ------------------------------------------------------------------- db side
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex|truncate|grant|load_extension)\b",
    re.I,
)


def _ro_conn() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{config.DB_PATH.as_posix()}?mode=ro", uri=True, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con


def list_tables() -> list[dict]:
    with _ro_conn() as con:
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
        return [{"table": n, "rows": con.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]} for n in names]


def describe_table(table: str, sample_rows: int = 3) -> dict:
    with _ro_conn() as con:
        valid = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if table not in valid:
            return {"error": f"Unknown table '{table}'. Valid tables: {sorted(valid)}"}
        cols = [{"name": r["name"], "type": r["type"], "pk": bool(r["pk"])} for r in con.execute(f'PRAGMA table_info("{table}")')]
        fks = [{"column": r["from"], "references": f'{r["table"]}.{r["to"]}'} for r in con.execute(f'PRAGMA foreign_key_list("{table}")')]
        sample = [dict(r) for r in con.execute(f'SELECT * FROM "{table}" LIMIT ?', (max(0, min(sample_rows, 5)),))]
        return {"table": table, "columns": cols, "foreign_keys": fks, "sample_rows": sample}


def validate_sql(sql: str) -> str | None:
    """Return an error message if the SQL is not a single read-only SELECT, else None."""
    s = sql.strip().rstrip(";").strip()
    if not s:
        return "Empty query."
    if ";" in s:
        return "Only a single statement is allowed."
    if not re.match(r"^(select|with)\b", s, re.I):
        return "Only SELECT queries (optionally starting with WITH) are allowed."
    if _FORBIDDEN.search(re.sub(r"'[^']*'", "''", s)):
        return "Query contains a forbidden keyword; this connection is read-only."
    return None


def run_sql(sql: str, max_rows: int | None = None) -> dict:
    err = validate_sql(sql)
    if err:
        return {"error": err}
    limit = min(max_rows or config.SQL_MAX_ROWS, config.SQL_MAX_ROWS)
    start = time.monotonic()
    try:
        with _ro_conn() as con:
            con.set_progress_handler(lambda: 1 if time.monotonic() - start > 5 else 0, 10000)  # 5 s timeout
            cur = con.execute(sql.strip().rstrip(";"))
            rows = cur.fetchmany(limit + 1)
            cols = [d[0] for d in cur.description] if cur.description else []
    except sqlite3.Error as e:
        return {"error": f"SQL error: {e}"}
    truncated = len(rows) > limit
    rows = rows[:limit]
    return {
        "columns": cols,
        "rows": [list(r) for r in rows],
        "row_count": len(rows),
        "truncated": truncated,
        "note": f"Truncated to {limit} rows." if truncated else "",
    }


def schema_summary() -> str:
    """Compact schema text for prompts (agent router / SQL generation)."""
    lines = []
    for t in list_tables():
        d = describe_table(t["table"], 0)
        cols = ", ".join(f'{c["name"]} {c["type"]}' for c in d["columns"])
        fks = "; ".join(f'{f["column"]}->{f["references"]}' for f in d["foreign_keys"])
        lines.append(f'{t["table"]}({cols})' + (f"  FK: {fks}" if fks else ""))
    return "\n".join(lines)
