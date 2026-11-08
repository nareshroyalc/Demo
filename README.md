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
Optional locally, required when hosted: `MCP_TOKEN` (Bearer token for `/mcp`) and `APP_PASSWORD` (UI and `/agent`).

## Deploy on Render (free)

1. Push this repo to GitHub, then in Render: **New > Blueprint**, pick the repo ([render.yaml](render.yaml) does the rest).
2. When asked, paste your `GEMINI_API_KEY` (never commit it). Render generates `MCP_TOKEN` and `APP_PASSWORD`; read them under the service's **Environment** tab.
3. Open `https://<name>.onrender.com`: the browser asks for a password (any username, password = `APP_PASSWORD`).
4. Connect Claude Code:
   ```
   claude mcp add --transport http brightline https://<name>.onrender.com/mcp --header "Authorization: Bearer <MCP_TOKEN>"
   ```

Free-tier behaviour: the service sleeps after 15 min idle (first request takes ~30-60 s), and the disk is wiped on restart,
so the app re-embeds the 5 PDFs automatically at startup (a few seconds, needs `GEMINI_API_KEY`).
`/agent` is rate-limited per IP (`AGENT_RATE_PER_MIN`, default 8) to protect the Gemini quota.

### Connect from the claude.ai website / Claude Desktop (custom connector)

The connector form cannot send custom headers, so `/mcp` also accepts the token in the URL:
`https://<name>.onrender.com/mcp?token=<MCP_TOKEN>`. Treat that URL as a secret (the app redacts it from its own logs).

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
