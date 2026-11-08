"""The /agent endpoint: retrieval + generation.

A small tool-calling loop on Gemini. It calls the SAME retrieval functions the MCP server exposes, loads the
SKILL.md playbooks into its system prompt, and returns the answer plus a step trace and sources for the UI.
"""
from __future__ import annotations

import json
import re

from . import config, embeddings, retrieval

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


def system_prompt() -> str:
    skills = load_skills()
    playbooks = "\n\n".join(f"## Skill: {s['name']}\nWhen to use: {s['description']}\n{s['body']}" for s in skills)
    return f"""You are the Brightline Supplies assistant. Brightline is a fictional B2B office-supplies company.
You answer questions using two sources, via tools:
  - Policy PDFs (returns, shipping SLA, pricing, support handbook, warranty): search_docs, get_document_page, list_documents
  - Operational SQLite database (customers, orders, order_items, products, shipments, support_tickets): list_tables, describe_table, run_sql

Rules:
- Ground every answer in tool results. Never invent policy numbers or data.
- Decide which source(s) the question needs; mixed questions need both (rule from docs, facts from SQL).
- Cite documents inline as [Title, p.N]. For data, state the filters you used.
- Be concise. Use a small markdown table for tabular results. If something is not in the sources, say so.
- Today's date is 2026-11-08.

Follow these playbooks:

{playbooks}"""


# ------------------------------------------------------------------- tool glue
def _decl():
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
def run_agent(question: str, history: list[dict] | None = None) -> dict:
    """history: [{role: 'user'|'assistant', text: str}, ...] (prior turns, text only)."""
    if not embeddings.available():
        return {
            "answer": "The agent needs a Gemini key. Add GEMINI_API_KEY to the .env file and restart the server. "
            "(The /mcp tools still work without it, using keyword search.)",
            "steps": [],
            "sources": [],
            "error": "no_api_key",
        }
    from google.genai import types

    contents = []
    for h in (history or [])[-8:]:
        role = "user" if h.get("role") == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=h.get("text", ""))]))
    contents.append(types.Content(role="user", parts=[types.Part(text=question)]))

    cfg = types.GenerateContentConfig(system_instruction=system_prompt(), tools=[_decl()], temperature=0.2)
    steps: list[dict] = []
    sources: dict[str, dict] = {}

    for _ in range(MAX_STEPS):
        resp = embeddings.client().models.generate_content(model=config.CHAT_MODEL, contents=contents, config=cfg)
        calls = resp.function_calls or []
        if not calls:
            return {"answer": (resp.text or "").strip(), "steps": steps, "sources": list(sources.values())}

        contents.append(resp.candidates[0].content)
        parts = []
        for c in calls:
            args = dict(c.args or {})
            result = _dispatch(c.name, args)
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
    }
