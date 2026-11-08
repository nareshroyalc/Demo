"""FastAPI app: /mcp (retrieval-only MCP), /agent (retrieval + generation), plus small JSON APIs and the UI.

Run:  python -m uvicorn app.main:app --port 8000
"""
from __future__ import annotations

import asyncio
import base64
import contextlib
import logging
import re
import secrets
import time
from collections import defaultdict, deque

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, config, embeddings, ingest, personas, retrieval
from .mcp_server import mcp


def _ensure_index() -> None:
    """Hosted disks (e.g. Render free) are wiped on restart: rebuild the vector index if it is missing."""
    if not embeddings.available():
        return
    try:
        q = retrieval.get_qdrant()
        if q.collection_exists(config.COLLECTION) and q.count(config.COLLECTION).count > 0:
            return
        print("startup: vector index missing, re-indexing PDFs ...", flush=True)
        print("startup:", ingest.ingest(lambda *_: None), flush=True)
    except Exception as e:  # never block startup; keyword search still works
        print(f"startup: indexing failed ({e}); falling back to keyword search", flush=True)


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    await asyncio.to_thread(_ensure_index)
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Brightline RAG", lifespan=lifespan)

_hits: dict[str, deque] = defaultdict(deque)


class _RedactToken(logging.Filter):
    """The connector URL carries ?token=...; never let it reach the access logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple):
            record.args = tuple(re.sub(r"(token=)[^&\s]+", r"***", a) if isinstance(a, str) else a for a in record.args)
        return True


logging.getLogger("uvicorn.access").addFilter(_RedactToken())


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    return fwd.split(",")[0].strip() if fwd else (request.client.host if request.client else "?")


def _basic_ok(header: str | None) -> bool:
    if not header or not header.lower().startswith("basic "):
        return False
    try:
        _, _, pw = base64.b64decode(header[6:]).decode().partition(":")
    except Exception:
        return False
    return secrets.compare_digest(pw.encode(), config.APP_PASSWORD.encode())


# ---- access control -------------------------------------------------------------------------
#   /health         open (platform health checks)
#   /mcp            MCP_TOKEN as Bearer header or ?token= query, for agents/clients
#   everything else HTTP Basic password (APP_PASSWORD), for people using the UI
#   /agent          additionally rate-limited per client IP (protects the Gemini quota)
@app.middleware("http")
async def access_control(request: Request, call_next):
    path = request.url.path
    if path == "/health":
        return await call_next(request)
    if path.startswith("/mcp"):
        if config.MCP_TOKEN:
            # Claude Code sends "Authorization: Bearer <token>"; the claude.ai connector UI cannot send
            # custom headers, so the same token is also accepted as ?token=<token> in the URL.
            ok = secrets.compare_digest(
                request.headers.get("authorization", "").encode(), f"Bearer {config.MCP_TOKEN}".encode()
            ) or secrets.compare_digest(request.query_params.get("token", "").encode(), config.MCP_TOKEN.encode())
            if not ok:
                return JSONResponse({"error": "unauthorized"}, status_code=401)
        return await call_next(request)
    if config.APP_PASSWORD and not _basic_ok(request.headers.get("authorization")):
        return JSONResponse(
            {"error": "password required"}, status_code=401, headers={"WWW-Authenticate": 'Basic realm="Brightline"'}
        )
    if path == "/agent" and request.method == "POST":
        now, window = time.monotonic(), _hits[_client_ip(request)]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= config.AGENT_RATE_PER_MIN:
            return JSONResponse({"answer": "Rate limit reached: please wait a minute and try again.", "steps": [], "sources": [], "error": "rate_limited"})
        window.append(now)
    return await call_next(request)


# ---- agent ---------------------------------------------------------------------------------
class AskBody(BaseModel):
    question: str
    history: list[dict] = []
    thread_id: str | None = None  # LangGraph engine only: server-side conversation memory
    persona: str | None = None  # persona id from /api/personas (default: generalist)


_engine = {"name": None, "run": None}


def _get_runner():
    """LangGraph by default (AGENT_ENGINE=plain forces the hand-written loop). Falls back to plain if LangGraph
    cannot be imported, so retrieval and /mcp never depend on it."""
    if _engine["run"] is None:
        if config.AGENT_ENGINE == "langgraph":
            try:
                from . import agent_graph

                _engine.update(name="langgraph", run=agent_graph.run_agent)
            except Exception as e:
                print(f"agent: LangGraph unavailable ({e}); using the plain engine", flush=True)
        if _engine["run"] is None:
            _engine.update(name="plain", run=agent.run_agent)
    return _engine["run"]


@app.post("/agent")
async def agent_endpoint(body: AskBody):
    if not body.question.strip():
        raise HTTPException(400, "question is required")
    try:
        personas.get_persona(body.persona)
    except KeyError:
        raise HTTPException(400, f"unknown persona '{body.persona}'")  # validated outside the catch-all below
    try:
        run = _get_runner()
        if _engine["name"] == "langgraph":
            return await asyncio.to_thread(run, body.question, body.history, body.thread_id, body.persona)
        return await asyncio.to_thread(run, body.question, body.history, body.persona)
    except Exception as e:  # surface model/API errors to the UI instead of a bare 500
        return JSONResponse({"answer": f"Agent error: {e}", "steps": [], "sources": [], "error": "agent_failed"}, status_code=200)


# ---- small JSON APIs for the UI ---------------------------------------------------------------
@app.get("/health")
def health():
    return {"ok": True, "gemini_key": embeddings.available(), "agent_engine": _engine["name"] or config.AGENT_ENGINE, "chat_model": config.CHAT_MODEL, "embed_model": config.EMBED_MODEL}


@app.get("/api/documents")
def api_documents():
    return retrieval.list_documents()


@app.get("/api/documents/{name}/file")
def api_document_file(name: str):
    path = config.DOCS_DIR / name
    if path.parent != config.DOCS_DIR or not path.exists() or path.suffix != ".pdf":
        raise HTTPException(404, "not found")
    return FileResponse(path, media_type="application/pdf")


@app.get("/api/search")
def api_search(q: str, k: int = 5):
    return retrieval.search_docs(q, k)


@app.get("/api/tables")
def api_tables():
    return retrieval.list_tables()


@app.get("/api/tables/{name}")
def api_table(name: str):
    info = retrieval.describe_table(name, 0)
    if "error" in info:
        raise HTTPException(404, info["error"])
    info["rows"] = retrieval.run_sql(f'SELECT * FROM "{name}"', 100)
    return info


@app.get("/api/personas")
def api_personas():
    return personas.load_personas()


@app.get("/api/skills")
def api_skills():
    return agent.load_skills()


@app.post("/api/ingest")
async def api_ingest():
    return await asyncio.to_thread(ingest.ingest, lambda *_: None)


# ---- UI + MCP routes ----------------------------------------------------------------------------
@app.get("/")
def index():
    return FileResponse(config.UI_DIR / "index.html")


if config.UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=config.UI_DIR), name="ui")

# FastMCP's streamable-HTTP app serves exactly one route, /mcp. Adding its routes to this app keeps the
# MCP endpoint at /mcp (no trailing-slash redirect) next to everything else.
app.router.routes.extend(mcp.streamable_http_app().routes)
