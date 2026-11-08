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
from . import config, embeddings, personas, prompt_cache, retrieval

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
_graphs: dict[str, Any] = {}  # one compiled graph per persona
_memory = MemorySaver()  # in-process conversation memory (per thread_id). SmartHub uses a Postgres checkpointer.
_cached_llms: dict[str, Any] = {}


def _cached_llm(cache_name: str):
    """A model that reads its system prompt + tool declarations from the named prompt cache."""
    if cache_name not in _cached_llms:
        if len(_cached_llms) > 8:  # caches rotate with the TTL; keep this small
            _cached_llms.clear()
        _cached_llms[cache_name] = ChatGoogleGenerativeAI(
            model=config.CHAT_MODEL, api_key=config.GEMINI_API_KEY, temperature=0.2, cached_content=cache_name
        )
    return _cached_llms[cache_name]


def build_graph(persona_id: str | None = None):
    """Compile (once per persona) the agent graph. Nodes: agent (LLM with the persona's tools bound) and tools
    (executes only those tools: anything else is unknown to the ToolNode and is refused)."""
    p = personas.get_persona(persona_id)
    if p["id"] in _graphs:
        return _graphs[p["id"]]

    tools = [t for t in TOOLS if t.name in p["tools"]]
    llm = ChatGoogleGenerativeAI(model=config.CHAT_MODEL, api_key=config.GEMINI_API_KEY, temperature=0.2).bind_tools(tools)
    prompt_text = plain_agent.system_prompt(p)
    system = SystemMessage(content=prompt_text)
    decl = plain_agent._decl(p["tools"])  # the same tool declarations, as the TTL cache stores them

    def agent_node(state: MessagesState):
        # Stable prefix (system prompt + tools) from the TTL prompt cache when available. A cached request must not
        # also carry the system message or bound tools, so it uses a plain model pointing at the cache.
        name = prompt_cache.get(p, prompt_text, decl)
        if name:
            try:
                msg = _cached_llm(name).invoke(state["messages"])
                msg.additional_kwargs["via_prompt_cache"] = True
                return {"messages": [msg]}
            except Exception:
                prompt_cache.invalidate(p["id"])  # cache gone/expired early: fall through to the full prompt
        return {"messages": [llm.invoke([system, *state["messages"]])]}

    g = StateGraph(MessagesState)
    g.add_node("agent", agent_node)
    g.add_node("tools", ToolNode(tools))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", tools_condition, {"tools": "tools", END: END})  # tool calls? run them : finish
    g.add_edge("tools", "agent")  # after tools, think again
    _graphs[p["id"]] = g.compile(checkpointer=_memory)
    return _graphs[p["id"]]


def graph_mermaid(persona_id: str | None = None) -> str:
    """Mermaid diagram of the graph, for docs and slides."""
    return build_graph(persona_id).get_graph().draw_mermaid()


# ------------------------------------------------------------------ run
def _text(msg: AIMessage) -> str:
    c = msg.content
    if isinstance(c, str):
        return c.strip()
    return "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c).strip()


STEP_LIMIT_ANSWER = "I could not finish within the step limit. Try a narrower question."


def _chunk_text(chunk) -> str:
    """Text of a streamed chunk (no stripping: whitespace between tokens matters)."""
    c = chunk.content
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
    return ""


def _no_key(p: dict) -> dict:
    return {
        "answer": "The agent needs a Gemini key. Add GEMINI_API_KEY to the .env file and restart the server. "
        "(The /mcp tools still work without it, using keyword search.)",
        "steps": [], "sources": [], "error": "no_api_key", "engine": "langgraph", "persona": p["id"],
    }


def _prepare(question: str, history: list[dict] | None, thread_id: str | None, persona: str | None):
    """Persona, compiled graph, thread id, input messages and run config, shared by run_agent and stream_agent."""
    p = personas.get_persona(persona)
    graph = build_graph(p["id"])
    tid = f"{p['id']}:{thread_id}" if thread_id else f"adhoc-{uuid.uuid4()}"  # memory is per persona
    msgs: list = []
    if not thread_id:
        for h in (history or [])[-8:]:
            cls = HumanMessage if h.get("role") == "user" else AIMessage
            msgs.append(cls(content=h.get("text", "")))
    msgs.append(HumanMessage(content=question))
    cfg = {"configurable": {"thread_id": tid}, "recursion_limit": MAX_STEPS * 2 + 1}
    return p, graph, tid, msgs, cfg


def _build_result(turn: list, p: dict, thread_id: str | None, tid: str) -> dict:
    """Trace (steps, sources, usage) and answer for ONE turn: the messages after the last human message."""
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

    usage = {"calls": 0, "prompt_tokens": 0, "cached_tokens": 0}
    for m in turn:
        if isinstance(m, AIMessage) and m.usage_metadata:
            usage["calls"] += 1
            usage["prompt_tokens"] += m.usage_metadata.get("input_tokens", 0)
            usage["cached_tokens"] += (m.usage_metadata.get("input_token_details") or {}).get("cache_read", 0)
    via_cache = any(isinstance(m, AIMessage) and m.additional_kwargs.get("via_prompt_cache") for m in turn)

    final = next((m for m in reversed(turn) if isinstance(m, AIMessage) and not m.tool_calls), None)
    return {"answer": _text(final) if final else "", "steps": steps, "sources": list(sources.values()),
            "engine": "langgraph", "persona": p["id"], "thread_id": thread_id or tid,
            "usage": {**usage, "prompt_cache": via_cache}}


def run_agent(
    question: str, history: list[dict] | None = None, thread_id: str | None = None, persona: str | None = None
) -> dict:
    """Same contract as agent.run_agent. If thread_id is given, memory comes from the checkpointer and
    `history` is ignored; otherwise a fresh thread is used and `history` (text turns) is replayed."""
    p = personas.get_persona(persona)
    if not embeddings.available():
        return _no_key(p)
    p, graph, tid, msgs, cfg = _prepare(question, history, thread_id, persona)
    try:
        state = graph.invoke({"messages": msgs}, cfg)
    except Exception as e:
        if "recursion" in str(e).lower():
            return {"answer": STEP_LIMIT_ANSWER, "steps": [], "sources": [], "engine": "langgraph", "persona": p["id"]}
        raise
    all_msgs = state["messages"]
    start = max(i for i, m in enumerate(all_msgs) if isinstance(m, HumanMessage))
    return _build_result(all_msgs[start + 1:], p, thread_id, tid)


def _tool_result_event(m: ToolMessage) -> dict:
    raw = getattr(m, "artifact", None)
    ev = {"type": "result", "tool": m.name}
    if isinstance(raw, dict):
        if m.name == "run_sql":
            ev["rows"], ev["error"] = raw.get("row_count"), raw.get("error")
        elif m.name == "search_docs":
            ev["passages"] = len(raw.get("results", []))
        if raw.get("error") and not ev.get("error"):
            ev["error"] = raw["error"]
    return ev


def stream_agent(
    question: str, history: list[dict] | None = None, thread_id: str | None = None, persona: str | None = None
):
    """The same run as run_agent, as a generator of events for /agent/stream:

      start -> ( token* -> step -> result )* -> token* -> done

    `token` events are the model's words as they are written; `step` fires when the model asks for a tool,
    `result` when the tool has finished; `done` carries the full result (same as run_agent). Tokens written
    before a `step` were a draft: clients clear the draft when a step arrives.
    Streaming costs nothing extra: it is the same model calls, delivered as they happen.
    """
    p = personas.get_persona(persona)
    if not embeddings.available():
        yield {"type": "done", **_no_key(p)}
        return
    p, graph, tid, msgs, cfg = _prepare(question, history, thread_id, persona)
    yield {"type": "start", "persona": p["id"], "engine": "langgraph"}
    turn: list = []
    try:
        for mode, payload in graph.stream({"messages": msgs}, cfg, stream_mode=["updates", "messages"]):
            if mode == "messages":
                chunk, meta = payload
                if meta.get("langgraph_node") == "agent":
                    text = _chunk_text(chunk)
                    if text:
                        yield {"type": "token", "text": text}
            elif mode == "updates":
                for out in payload.values():
                    for m in (out.get("messages", []) if isinstance(out, dict) else []):
                        turn.append(m)
                        if isinstance(m, AIMessage):
                            for tc in m.tool_calls or []:
                                yield {"type": "step", "tool": tc["name"], "args": tc["args"], "id": tc["id"]}
                        elif isinstance(m, ToolMessage):
                            yield _tool_result_event(m)
    except Exception as e:
        if "recursion" in str(e).lower():
            yield {"type": "done", "answer": STEP_LIMIT_ANSWER, "steps": [], "sources": [], "engine": "langgraph", "persona": p["id"]}
            return
        raise
    yield {"type": "done", **_build_result(turn, p, thread_id, tid)}
