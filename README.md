# Brightline RAG Agent (demo)

A RAG agent over **5 policy PDFs** and **1 SQLite database**, with two doors:

| Endpoint | What it does |
|---|---|
| `POST /agent` | Full agent: routes between docs and DB, retrieves, **Gemini writes the answer** with citations |
| `/mcp` | **Retrieval only** (no LLM). Other agents (Claude Code, Claude Desktop, ...) plug in and reason themselves |

Both use the same retrieval layer ([app/retrieval.py](app/retrieval.py)). Vectors live in **Qdrant local mode** (`data/qdrant/`, no server).

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env        # then put your GEMINI_API_KEY in .env
.\.venv\Scripts\python.exe scripts\generate_demo_data.py   # 5 PDFs + data\demo.db (already generated)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
```

Open http://127.0.0.1:8000, go to **Documents**, click **Re-index PDFs** (embeds with Gemini into Qdrant), then ask questions in **Chat**.
Without a key, `/mcp` and keyword search still work; `/agent` explains that a key is needed.

## Use from Claude Code

```powershell
claude mcp add --transport http brightline http://127.0.0.1:8000/mcp
# or load the whole plugin (MCP config + skills):
claude --plugin-dir .
```

Tools: `search_docs`, `list_documents`, `get_document_page`, `list_tables`, `describe_table`, `run_sql` (read-only).
Skills: `docs-research`, `sql-analyst`, `docs-plus-data` in [skills/](skills/).
Optional: set `MCP_TOKEN` in `.env` to require `Authorization: Bearer <token>` on `/mcp`.

## Try these questions

- Docs only: "What is the refund window for damaged items?"
- Data only: "Top 5 customers by revenue, excluding cancelled orders."
- Both: "Which delivered orders were late, and what compensation does policy give per lateness band?"

## Layout

```
app/        retrieval.py (shared) · mcp_server.py (/mcp) · agent.py (/agent) · ingest.py · main.py
skills/     SKILL.md playbooks (used by the agent AND by Claude Code)
ui/         React app (no build step), served at /
scripts/    generate_demo_data.py · test_mcp_client.py · smoke_retrieval.py
data/       docs/*.pdf · demo.db · qdrant/ (created on indexing)
```

## Safety notes

- `run_sql` opens SQLite read-only, allows a single SELECT/WITH, rejects write keywords, caps rows (200) and time (5 s).
- Retrieved PDF text is untrusted data; skills tell the model to ground answers in tool results.
- PDF text is sent to the Gemini API for embeddings and answers: do not use confidential documents on a free tier.
