"""FastAPI app: /mcp (retrieval-only MCP), /agent (retrieval + generation), plus small JSON APIs and the UI.

Run:  python -m uvicorn app.main:app --port 8000
"""
from __future__ import annotations

import asyncio
import contextlib

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import agent, config, embeddings, ingest, retrieval
from .mcp_server import mcp


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Brightline RAG", lifespan=lifespan)


# ---- optional bearer-token guard for /mcp -------------------------------------------------
@app.middleware("http")
async def guard_mcp(request: Request, call_next):
    if config.MCP_TOKEN and request.url.path.startswith("/mcp"):
        if request.headers.get("authorization") != f"Bearer {config.MCP_TOKEN}":
            return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)


# ---- agent ---------------------------------------------------------------------------------
class AskBody(BaseModel):
    question: str
    history: list[dict] = []


@app.post("/agent")
async def agent_endpoint(body: AskBody):
    if not body.question.strip():
        raise HTTPException(400, "question is required")
    try:
        return await asyncio.to_thread(agent.run_agent, body.question, body.history)
    except Exception as e:  # surface model/API errors to the UI instead of a bare 500
        return JSONResponse({"answer": f"Agent error: {e}", "steps": [], "sources": [], "error": "agent_failed"}, status_code=200)


# ---- small JSON APIs for the UI ---------------------------------------------------------------
@app.get("/health")
def health():
    return {"ok": True, "gemini_key": embeddings.available(), "chat_model": config.CHAT_MODEL, "embed_model": config.EMBED_MODEL}


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
