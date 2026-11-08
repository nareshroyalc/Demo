"""The /agent endpoint: retrieval + generation.

A small tool-calling loop on Gemini. It calls the SAME retrieval functions the MCP server exposes, loads the
SKILL.md playbooks into its system prompt, and returns the answer plus a step trace and sources for the UI.
"""
from __future__ import annotations

import json
import re

from . import config, embeddings, personas, prompt_cache, retrieval

MAX_STEPS = 8
MAX_TOOL_CHARS = 7000


# ---------------------------------------------------------------------- skills
def load_skills() -> list[dict]:
    """Read skills/*/SKILL.md (frontmatter: name, description)."""
    out = []
    for path in sorted(config.SKILLS_DIR.glob("*/SKILL.md")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        meta, body = (m.group(1), m.group(2).strip()) if m else ("", raw)
        fields = dict(re.findall(r"^(\w+):\s*(.+)$", meta, re.M))
        out.append(
            {
                "name": fields.get("name", path.parent.name),
                "description": fields.get("description", ""),
                "body": body,
                "path": str(path.relative_to(config.ROOT)).replace("\\", "/"),
            }
        )
    return out


def system_prompt(persona: dict | None = None) -> str:
    """Base rules + the persona's allowed sources, instructions and skills. With no persona (or the default
    generalist, which allows everything and has no extra instructions) this matches the original prompt."""
    persona = persona or personas.get_persona(None)
    allowed = persona["tools"]
    skills = [s for s in load_skills() if s["name"] in persona["skills"]]
    playbooks = "\n\n".join(f"## Skill: {s['name']}\nWhen to use: {s['description']}\n{s['body']}" for s in skills)

    doc_tools = [t for t in personas.DOC_TOOLS if t in allowed]
    db_tools = [t for t in personas.DB_TOOLS if t in allowed]
    sources = []
    if doc_tools:
        sources.append(f"  - Policy PDFs (returns, shipping SLA, pricing, support handbook, warranty): {', '.join(doc_tools)}")
    if db_tools:
        sources.append(f"  - Operational SQLite database (customers, orders, order_items, products, shipments, support_tickets): {', '.join(db_tools)}")
    if doc_tools and db_tools:
        routing = "- Decide which source(s) the question needs; mixed questions need both (rule from docs, facts from SQL)."
    else:
        routing = ("- You only have access to the source listed above. If the question needs the other source, answer what you can, "
                   "say clearly that you cannot access it in this role, and suggest switching persona. Never guess its content.")
    role = f"\n\n## Persona: {persona['name']}\n{persona['instructions']}" if persona["instructions"] else ""
    src_text = "\n".join(sources)
    n_sources = "two sources" if doc_tools and db_tools else "one source"

    return f"""You are the Brightline Supplies assistant. Brightline is a fictional B2B office-supplies company.
You answer questions using {n_sources}, via tools:
{src_text}

Rules:
- Ground every answer in tool results. Never invent policy numbers or data.
{routing}
- Cite documents inline as [Title, p.N]. For data, state the filters you used.
- Be concise. Use a small markdown table for tabular results. If something is not in the sources, say so.
- Today's date is 2026-11-08.{role}

Follow these playbooks:

{playbooks}"""


# ------------------------------------------------------------------- tool glue
def _decl_all():
    from google.genai import types

    S = types.Schema
    T = types.Type

    def fn(name, desc, props=None, required=None):
        return types.FunctionDeclaration(
            name=name,
            description=desc,
            parameters=S(type=T.OBJECT, properties=props or {}, required=required or []) if props else None,
        )

    return types.Tool(
        function_declarations=[
            fn(
                "search_docs",
                "Search the policy PDFs (hybrid vector+keyword). Returns passages with citations.",
                {
                    "query": S(type=T.STRING, description="Natural-language query with key terms."),
                    "k": S(type=T.INTEGER, description="Passages to return, 1-10 (default 5)."),
                },
                ["query"],
            ),
            fn("list_documents", "List policy documents with page counts."),
            fn(
                "get_document_page",
                "Read the full text of a page of a policy document.",
                {"doc": S(type=T.STRING, description="Filename, e.g. 02_shipping_and_delivery_sla.pdf"), "page": S(type=T.INTEGER)},
                ["doc", "page"],
            ),
            fn("list_tables", "List database tables with row counts."),
            fn(
                "describe_table",
                "Columns, foreign keys and sample rows for a table. Call before writing SQL.",
                {"table": S(type=T.STRING)},
                ["table"],
            ),
            fn(
                "run_sql",
                "Run one read-only SQLite SELECT. Late delivery = shipments.transit_business_days - shipments.sla_days > 0.",
                {"sql": S(type=T.STRING, description="A single SELECT statement.")},
                ["sql"],
            ),
        ]
    )


def _decl(allowed):
    """Only the persona's tools are offered to the model."""
    return _decl_all().model_copy(
        update={"function_declarations": [d for d in _decl_all().function_declarations if d.name in allowed]}
    )


def _dispatch(name: str, args: dict):
    if name == "search_docs":
        return {"results": retrieval.search_docs(args.get("query", ""), int(args.get("k", 5) or 5))}
    if name == "list_documents":
        return {"documents": retrieval.list_documents()}
    if name == "get_document_page":
        return retrieval.get_document_page(args.get("doc", ""), int(args.get("page", 1)))
    if name == "list_tables":
        return {"tables": retrieval.list_tables()}
    if name == "describe_table":
        return retrieval.describe_table(args.get("table", ""))
    if name == "run_sql":
        return retrieval.run_sql(args.get("sql", ""))
    return {"error": f"Unknown tool {name}"}


def _clip(obj) -> str:
    s = json.dumps(obj, default=str)
    return s if len(s) <= MAX_TOOL_CHARS else s[:MAX_TOOL_CHARS] + '..."[truncated]"'


# ------------------------------------------------------------------------ loop
def run_agent(question: str, history: list[dict] | None = None, persona: str | None = None) -> dict:
    """history: [{role: 'user'|'assistant', text: str}, ...] (prior turns, text only)."""
    p = personas.get_persona(persona)
    if not embeddings.available():
        return {
            "answer": "The agent needs a Gemini key. Add GEMINI_API_KEY to the .env file and restart the server. "
            "(The /mcp tools still work without it, using keyword search.)",
            "steps": [],
            "sources": [],
            "error": "no_api_key",
            "persona": p["id"],
        }
    from google.genai import types

    contents = []
    for h in (history or [])[-8:]:
        role = "user" if h.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=h.get("text", ""))]))
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

    sp, tool = system_prompt(p), _decl(p["tools"])
    full_cfg = types.GenerateContentConfig(system_instruction=sp, tools=[tool], temperature=0.2)
    # The stable prefix (system prompt + tools) comes from the TTL prompt cache when available. A request that
    # uses cached_content must NOT also send system_instruction/tools, so the two configs are separate.
    cache_name = prompt_cache.get(p, sp, tool)
    cfg = types.GenerateContentConfig(cached_content=cache_name, temperature=0.2) if cache_name else full_cfg
    steps: list[dict] = []
    sources: dict[str, dict] = {}
    usage = {"calls": 0, "prompt_tokens": 0, "cached_tokens": 0}

    for _ in range(MAX_STEPS):
        try:
            resp = embeddings.client().models.generate_content(model=config.CHAT_MODEL, contents=contents, config=cfg)
        except Exception:
            if not cache_name:
                raise
            prompt_cache.invalidate(p["id"])  # cache gone/expired early: retry once with the full prompt
            cache_name, cfg = None, full_cfg
            resp = embeddings.client().models.generate_content(model=config.CHAT_MODEL, contents=contents, config=cfg)
        um = resp.usage_metadata
        usage["calls"] += 1
        usage["prompt_tokens"] += (um.prompt_token_count or 0) if um else 0
        usage["cached_tokens"] += (um.cached_content_token_count or 0) if um else 0
        calls = resp.function_calls or []
        if not calls:
            return {"answer": (resp.text or "").strip(), "steps": steps, "sources": list(sources.values()),
                    "persona": p["id"], "usage": {**usage, "prompt_cache": bool(cache_name)}}

        contents.append(resp.candidates[0].content)
        parts = []
        for c in calls:
            args = dict(c.args or {})
            # second line of defence: refuse any tool outside the persona's scope, even if the model calls it
            result = (
                _dispatch(c.name, args)
                if c.name in p["tools"]
                else {"error": f"Tool '{c.name}' is not available to the {p['name']} persona."}
            )
            if c.name == "search_docs":
                for r in result.get("results", []):
                    sources.setdefault(r["citation"], {"citation": r["citation"], "doc": r["doc"], "page": r["page"], "snippet": r["text"][:240]})
            step = {"tool": c.name, "args": args}
            if c.name == "run_sql":
                step["rows"] = result.get("row_count")
                step["error"] = result.get("error")
            steps.append(step)
            parts.append(types.Part.from_function_response(name=c.name, response={"result": json.loads(_clip(result))}))
        contents.append(types.Content(role="user", parts=parts))

    return {
        "answer": "I could not finish within the step limit. Try a narrower question.",
        "steps": steps,
        "sources": list(sources.values()),
        "persona": p["id"],
        "usage": {**usage, "prompt_cache": bool(cache_name)},
    }
