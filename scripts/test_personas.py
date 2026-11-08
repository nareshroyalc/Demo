"""Verify personas: (1) structural tool scoping in both engines (no model calls), (2) live behaviour.

Run:  python scripts/test_personas.py            (structure only)
      python scripts/test_personas.py --live     (also asks the model; ~10 requests, paced for the free tier)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import agent, agent_graph, personas  # noqa: E402

fails = []


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        fails.append(name)


print("1) Structure: which tools each persona can reach")
for p in personas.load_personas():
    plain = {d.name for d in agent._decl(p["tools"]).function_declarations}
    graph_tools = set(agent_graph.build_graph(p["id"]).nodes["tools"].bound.tools_by_name)
    check(f"{p['id']}: plain engine offers exactly its tools", plain == set(p["tools"]), sorted(plain).__repr__())
    check(f"{p['id']}: langgraph engine offers exactly its tools", graph_tools == set(p["tools"]))
    prompt = agent.system_prompt(p)
    has_sql_text = "run_sql" in prompt.split("Follow these playbooks")[0]
    check(f"{p['id']}: prompt mentions SQL only if allowed", has_sql_text == ("run_sql" in p["tools"]))

try:
    personas.get_persona("nope")
    check("unknown persona rejected", False)
except KeyError:
    check("unknown persona rejected", True)

if "--live" in sys.argv:
    print("\n2) Live behaviour (paced for the Gemini free tier)")
    CASES = [
        ("policy-advisor", "Top 3 customers by revenue, excluding cancelled orders.",
         lambda r: "run_sql" not in [s["tool"] for s in r["steps"]], "policy-advisor cannot reach SQL"),
        ("data-analyst", "What is the refund window for damaged items?",
         lambda r: "search_docs" not in [s["tool"] for s in r["steps"]], "data-analyst cannot reach documents"),
        ("support-agent", "A Gold customer's order arrived 4 business days after the SLA. What are they owed, and what do I tell them?",
         lambda r: "10%" in r["answer"] and "suggested reply" in r["answer"].lower(), "support-agent applies the 3-5 day band (10%) and drafts a reply"),
        ("generalist", "What is the refund window for damaged items?",
         lambda r: "7 days" in r["answer"], "generalist unchanged (7 days)"),
    ]
    for pid, q, ok_fn, label in CASES:
        for engine, fn in (("langgraph", lambda q, pid=pid: agent_graph.run_agent(q, persona=pid)),):
            r = fn(q)
            tools = " > ".join(s["tool"] for s in r["steps"]) or "(no tools)"
            check(label, ok_fn(r), f"[{engine}] tools: {tools}")
            print("      answer:", " ".join(r["answer"].split())[:170])
            time.sleep(22)
    # one check on the plain engine too
    r = agent.run_agent("What is the refund window for damaged items?", persona="policy-advisor")
    check("plain engine + policy-advisor answers from documents", "7 days" in r["answer"], "tools: " + " > ".join(s["tool"] for s in r["steps"]))

print("\nRESULT:", "all checks passed" if not fails else f"FAILED: {fails}")
sys.exit(1 if fails else 0)
