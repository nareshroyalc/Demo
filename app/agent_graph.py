"""LangGraph version of the /agent endpoint.

Same job as app/agent.py (a hand-written loop), expressed as an explicit graph:

            +-------+   tool calls?   +-------+
   START -> | agent | --------------> | tools | --+
            +-------+ <---------------+-------+   |
                |  no tool calls                   |
                v                                  |
               END      (loop until done) <--------+

What it reuses unchanged:  app/retrieval.py (all retrieval), app/agent.system_prompt() (skills playbooks).
What LangGraph adds:       explicit state + nodes/edges, a checkpointer (conversation memory per thread_id),
                           a recursion limit as the step cap, and a graph you can draw.
Response shape is identical to agent.run_agent, so the UI and /agent API do not change.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from . import agent as plain_agent  # system_prompt() / skills only
from . import config, embeddings, retrieval

MAX_STEPS = plain_agent.MAX_STEPS
MAX_TOOL_CHARS = plain_agent.MAX_TOOL_CHARS


def _out(result: Any) -> tuple[str, Any]:
    """Tools return (text for the model, raw object for our step/source trace)."""
    s = json.dumps(result, default=str)
    return (s if len(s) <= MAX_TOOL_CHARS else s[:MAX_TOOL_CHARS] + ' ..."[truncated]"'), result


# ------------------------------------------------------------------ tools
# Thin wrappers over app/retrieval.py: the SAME functions the /mcp server exposes.
@tool(response_format="content_and_artifact")
def search_docs(query: str, k: int = 5):
    """Search the policy PDFs (returns, shipping SLA, pricing, support, warranty) with hybrid vector+keyword
    search. Returns passages with citations. Use for any rule, window, fee, SLA, discount or warranty question."""
    return _out({"results": retrieval.search_docs(query, int(k or 5))})


@tool(response_format="content_and_artifact")
def list_documents():
    """List the policy documents with page counts."""
    return _out({"documents": retrieval.list_documents()})


@tool(response_format="content_and_artifact")
def get_document_page(doc: str, page: int):
    """Read the full text of one page of a policy document (doc = filename like 02_shipping_and_delivery_sla.pdf)."""
    return _out(retrieval.get_document_page(doc, int(page)))


@tool(response_format="content_and_artifact")
def list_tables():
    """List database tables with row counts."""
    return _out({"tables": retrieval.list_tables()})


@tool(response_format="content_and_artifact")
def describe_table(table: str):
    """Columns, foreign keys and sample rows for a table. Call before writing SQL."""
    return _out(retrieval.describe_table(table))


@tool(response_format="content_and_artifact")
def run_sql(sql: str):
    """Run ONE read-only SQLite SELECT. Late delivery = shipments.transit_business_days - shipments.sla_days > 0."""
    return _out(retrieval.run_sql(sql))


TOOLS = [search_docs, list_documents, get_document_page, list_tables, describe_table, run_sql]

# ------------------------------------------------------------------ graph
_graph = None
_memory = MemorySaver()  # in-process conversation memory (per thread_id). SmartHub uses a Postgres checkpointer.


def build_graph():
    """Compile the agent graph once. Nodes: agent (LLM + tools bound) and tools (executes tool calls)."""
    global _graph
    if _graph is not None:
        return _graph

    llm = ChatGoogleGenerativeAI(model=config.CHAT_MODEL, api_key=config.GEMINI_API_KEY, temperature=0.2).bind_tools(TOOLS)
    system = SystemMessage(content=plain_agent.system_prompt())

    def agent_node(state: MessagesState):
        return {"messages": [llm.invoke([system, *state["messages"]])]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent_node)
    g.add_node("tools", ToolNode(TOOLS))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})  # tool calls? run them : finish
    g.add_edge("tools", "agent")  # after tools, think again
    _graph = g.compile(checkpointer=_memory)
    return _graph


def graph_mermaid() -> str:
    """Mermaid diagram of the graph, for docs and slides."""
    return build_graph().get_graph().draw_mermaid()


# ------------------------------------------------------------------ run
def _text(msg: AIMessage) -> str:
    c = msg.content
    if isinstance(c, str):
        return c.strip()
    return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c).strip()


def run_agent(question: str, history: list[dict] | None = None, thread_id: str | None = None) -> dict:
    """Same contract as agent.run_agent. If thread_id is given, memory comes from the checkpointer and
    `history` is ignored; otherwise a fresh thread is used and `history` (text turns) is replayed."""
    if not embeddings.available():
        return {
            "answer": "The agent needs a Gemini key. Add GEMINI_API_KEY to the .env file and restart the server. "
            "(The /mcp tools still work without it, using keyword search.)",
            "steps": [], "sources": [], "error": "no_api_key", "engine": "langgraph",
        }
    graph = build_graph()
    tid = thread_id or f"adhoc-{uuid.uuid4()}"
    msgs: list = []
    if not thread_id:
        for h in (history or [])[-8:]:
            cls = HumanMessage if h.get("role") == "user" else AIMessage
            msgs.append(cls(content=h.get("text", "")))
    msgs.append(HumanMessage(content=question))

    cfg = {"configurable": {"thread_id": tid}, "recursion_limit": MAX_STEPS * 2 + 1}
    try:
        state = graph.invoke({"messages": msgs}, cfg)
    except Exception as e:
        if "recursion" in str(e).lower():
            return {"answer": "I could not finish within the step limit. Try a narrower question.",
                    "steps": [], "sources": [], "engine": "langgraph"}
        raise

    # Build the trace for THIS turn only: everything after the last human message.
    all_msgs = state["messages"]
    start = max(i for i, m in enumerate(all_msgs) if isinstance(m, HumanMessage))
    turn = all_msgs[start + 1:]

    by_id = {m.tool_call_id: m for m in turn if isinstance(m, ToolMessage)}
    steps, sources = [], {}
    for m in turn:
        if not isinstance(m, AIMessage):
            continue
        for tc in m.tool_calls or []:
            step = {"tool": tc["name"], "args": tc["args"]}
            tm = by_id.get(tc["id"])
            raw = getattr(tm, "artifact", None) if tm else None
            if tc["name"] == "run_sql" and isinstance(raw, dict):
                step["rows"], step["error"] = raw.get("row_count"), raw.get("error")
            if tc["name"] == "search_docs" and isinstance(raw, dict):
                for r in raw.get("results", []):
                    sources.setdefault(r["citation"], {"citation": r["citation"], "doc": r["doc"], "page": r["page"], "snippet": r["text"][:240]})
            steps.append(step)

    final = next((m for m in reversed(turn) if isinstance(m, AIMessage) and not m.tool_calls), None)
    return {"answer": _text(final) if final else "", "steps": steps, "sources": list(sources.values()),
            "engine": "langgraph", "thread_id": tid}
