# Brightline RAG Agent (demo)

A RAG agent over **5 policy PDFs** and **1 SQLite database**, with two doors:

| Endpoint | What it does |
|---|---|
| `POST /agent` | Full agent: routes between docs and DB, retrieves, **Gemini writes the answer** with citations |
| `/mcp` | **Retrieval only** (no LLM). Other agents (Claude Code, Claude Desktop, ...) plug in and reason themselves |

Both use the same retrieval layer ([app/retrieval.py](app/retrieval.py)). Vectors live in **Qdrant local mode** (`data/qdrant/`, no server).

## Two agent engines (same retrieval, same skills, same API)

`/agent` runs on **LangGraph** by default ([app/agent_graph.py](app/agent_graph.py)): an explicit graph with an `agent` node (Gemini + tools), a `tools` node and a loop between them ([diagram](docs/agent_graph.mmd)), plus checkpointer memory when the request includes a `thread_id`.
Set `AGENT_ENGINE=plain` to use the original hand-written loop ([app/agent.py](app/agent.py)); the app also falls back to it automatically if LangGraph cannot load.
Compare both on the same questions: `python scripts/compare_engines.py`.
Note: the Gemini free tier allows about 15 requests/min, and one question uses 2-6 requests.

## Personas

A persona is a role: extra instructions + the tools it may use + the skills it follows, defined in [personas/](personas/) as markdown files
(`generalist` default, `support-agent`, `data-analyst`, `policy-advisor`). Pick one in the chat box, or send `"persona": "<id>"` to `/agent`
(list them at `/api/personas`).

Tool scope is enforced by the server, as in SmartHub: tools outside a persona's list are never offered to the model and are refused if called.
The default persona produces exactly the original prompt, so existing behaviour is unchanged. Retrieval and `/mcp` do not use personas.
Test: `python scripts/test_personas.py` (structure) and `--live` (asks the model; about 10 requests).

## Streaming

`POST /agent/stream` runs the same agent as `/agent` but sends **server-sent events** while it works: `start`, `step` (a tool is called), `result` (the tool finished),
`token` (answer words) and `done` (the full result, same shape as `/agent`). The chat page uses it, so tool calls appear live and the answer types out.
It makes the same model calls as `/agent`, so it costs nothing extra. The LangGraph engine streams the words; the plain engine streams the steps and sends the final
text in one piece. `/agent` is unchanged. Try it: `python scripts/test_stream.py "your question" [persona]` (server on port 8010).

## Prompt cache (TTL)

The prompt that is identical on every request (system prompt + persona + skills + tool definitions) can be stored in a Gemini **explicit cache with a TTL**
([app/prompt_cache.py](app/prompt_cache.py)), one cache per persona, refreshed before it expires and rebuilt when a skill or persona file changes.
`PROMPT_CACHE=auto` (default) tries it; `PROMPT_CACHE=off` disables it; `PROMPT_CACHE_TTL_SECONDS` sets the TTL (default 3600).

It is an optimisation, never a dependency: if the API refuses (the free-tier key we tested returns 404 for the caches endpoint, or the prompt is below the
model's minimum size), the agent sends the full prompt as before and does not retry for 30 minutes. `/health` shows the cache status and `/agent` returns
`usage` (prompt tokens, cached tokens, whether the cache was used). Gemini's automatic (implicit) caching still applies once a prefix is large enough.
Tests: `python scripts/test_prompt_cache.py` (logic and request shapes, no key needed) and `--live`.

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
