"""PDF -> page text -> chunks -> embeddings -> Qdrant (local mode). Also builds a chunk cache for BM25."""
from __future__ import annotations

import json
import re
import uuid

from pypdf import PdfReader

from . import config, embeddings

CHUNK_CACHE = config.ROOT / "data" / "chunks.json"


def _split(text: str) -> list[str]:
    """Paragraph-aware chunking with overlap. Pages are short, so most pages yield 1-3 chunks."""
    text = re.sub(r"[ \t]+", " ", text).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d+\.\s)", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if cur and len(cur) + len(p) + 1 > config.CHUNK_CHARS:
            chunks.append(cur)
            cur = cur[-config.CHUNK_OVERLAP :] + "\n" + p
        else:
            cur = (cur + "\n" + p).strip() if cur else p
        while len(cur) > config.CHUNK_CHARS * 1.6:  # a single huge paragraph
            chunks.append(cur[: config.CHUNK_CHARS])
            cur = cur[config.CHUNK_CHARS - config.CHUNK_OVERLAP :]
    if cur.strip():
        chunks.append(cur)
    return chunks


def parse_docs() -> list[dict]:
    rows: list[dict] = []
    for pdf in sorted(config.DOCS_DIR.glob("*.pdf")):
        reader = PdfReader(str(pdf))
        meta_title = (reader.metadata.title if reader.metadata else None) or pdf.stem
        for page_no, page in enumerate(reader.pages, 1):
            for idx, chunk in enumerate(_split(page.extract_text() or "")):
                rows.append(
                    {
                        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{pdf.name}:{page_no}:{idx}")),
                        "doc": pdf.name,
                        "title": meta_title,
                        "page": page_no,
                        "text": chunk,
                    }
                )
    return rows


def ingest(progress=print) -> dict:
    """Rebuild the whole index. Safe to re-run (collection is recreated)."""
    from qdrant_client.models import Distance, PointStruct, VectorParams

    from .retrieval import get_qdrant, reset_caches

    rows = parse_docs()
    if not rows:
        raise RuntimeError(f"No PDFs found in {config.DOCS_DIR}")
    CHUNK_CACHE.write_text(json.dumps(rows), encoding="utf-8")
    progress(f"parsed {len(rows)} chunks from {len({r['doc'] for r in rows})} PDFs")

    vectors_done = 0
    if embeddings.available():
        q = get_qdrant()
        if q.collection_exists(config.COLLECTION):
            q.delete_collection(config.COLLECTION)
        q.create_collection(
            config.COLLECTION,
            vectors_config=VectorParams(size=config.EMBED_DIM, distance=Distance.COSINE),
        )
        vecs = embeddings.embed_documents([r["text"] for r in rows])
        q.upsert(
            config.COLLECTION,
            points=[
                PointStruct(id=r["id"], vector=v, payload={k: r[k] for k in ("doc", "title", "page", "text")})
                for r, v in zip(rows, vecs)
            ],
        )
        vectors_done = len(vecs)
        progress(f"embedded + stored {vectors_done} vectors in Qdrant")
    else:
        progress("GEMINI_API_KEY not set: skipped embeddings (keyword search only)")

    reset_caches()
    return {"documents": len({r["doc"] for r in rows}), "chunks": len(rows), "vectors": vectors_done}


if __name__ == "__main__":
    print(ingest())
