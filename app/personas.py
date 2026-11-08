"""Personas: a role for the agent = instructions + allowed tools + allowed skills.

Files: personas/<id>.md  (frontmatter: name, description, tools, skills; body = extra instructions).

Like SmartHub, tool scope is enforced in the BACKEND, not only in the prompt: tools outside the persona's list
are never offered to the model, and are refused if called anyway (see agent.py / agent_graph.py).
Retrieval is untouched: a persona only decides which of the existing tools the agent may use.
"""
from __future__ import annotations

import re

from . import config

PERSONAS_DIR = config.ROOT / "personas"
DEFAULT_ID = "generalist"
ALL_TOOLS = ("search_docs", "list_documents", "get_document_page", "list_tables", "describe_table", "run_sql")
DOC_TOOLS = ("search_docs", "get_document_page", "list_documents")  # order matches the original prompt
DB_TOOLS = ("list_tables", "describe_table", "run_sql")


def _csv(v: str) -> list[str]:
    return [x.strip() for x in v.split(",") if x.strip()]


def load_personas() -> list[dict]:
    out = []
    for path in sorted(PERSONAS_DIR.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", raw, re.S)
        meta, body = (m.group(1), m.group(2).strip()) if m else ("", raw.strip())
        f = dict(re.findall(r"^(\w+):\s*(.+?)\s*$", meta, re.M))
        tools = [t for t in _csv(f.get("tools", "")) if t in ALL_TOOLS]  # unknown names are ignored
        out.append(
            {
                "id": path.stem,
                "name": f.get("name", path.stem),
                "description": f.get("description", ""),
                "tools": tools,
                "skills": _csv(f.get("skills", "")),
                "instructions": body,
            }
        )
    return out


def get_persona(persona_id: str | None) -> dict:
    """Return the persona (default: generalist). Raises KeyError for an unknown id."""
    pid = persona_id or DEFAULT_ID
    for p in load_personas():
        if p["id"] == pid:
            return p
    raise KeyError(pid)
