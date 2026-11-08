"""Run the same questions through BOTH agent engines and compare tools used, answers and key facts.

Run:  python scripts/compare_engines.py
(No server needed; the Qdrant folder must not be in use by a running server.)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import agent, agent_graph  # noqa: E402

QS = [  # (kind, question, facts that must appear in the answer)
    ("docs", "What is the refund window for damaged items, and who pays return shipping?", ["7 days"]),
    ("data", "Top 3 customers by revenue, excluding cancelled orders.", ["Zenith Associates", "Xenon Group", "Fairway Solutions"]),
    ("both", "Which delivered orders were late, and what compensation credit does the policy give per lateness band? Give counts per band.",
     ["20", "17", "13", "5%", "10%", "15%"]),
]
bad = 0
for kind, q, must in QS:
    print(f"\n=== [{kind}] {q}")
    for name, fn in (("plain", agent.run_agent), ("langgraph", agent_graph.run_agent)):
        t = time.time()
        r = fn(q)
        time.sleep(25)  # stay under the Gemini free-tier limit (15 requests/min)
        miss = [m for m in must if m not in r["answer"]]
        bad += bool(miss)
        print(f"  {name:9} {time.time()-t:5.1f}s  tools: {' > '.join(s['tool'] for s in r['steps'])}")
        print(f"  {'':9} facts present: {'ALL' if not miss else 'MISSING ' + str(miss)}   sources: {len(r['sources'])}")
print("\nRESULT:", "all key facts present in both engines" if not bad else f"{bad} engine-answers missing facts")
sys.exit(1 if bad else 0)
