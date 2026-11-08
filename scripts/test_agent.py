"""Ask the running /agent endpoint a docs-only, a data-only and a combined question."""
import json
import sys
import urllib.request

QS = [
    "What is the refund window for damaged items, and who pays return shipping?",
    "Top 3 customers by revenue, excluding cancelled orders.",
    "Which delivered orders were late, and what compensation credit does the policy give per lateness band? Give counts per band.",
]
for q in (sys.argv[1:] or QS):
    req = urllib.request.Request(
        "http://127.0.0.1:8000/agent", json.dumps({"question": q}).encode(), {"Content-Type": "application/json"}
    )
    r = json.load(urllib.request.urlopen(req, timeout=170))
    print("=== Q:", q)
    print("TOOLS:", " > ".join(s["tool"] + (f"[{s['error']}]" if s.get("error") else "") for s in r["steps"]))
    print(r["answer"])
    print("SOURCES:", "; ".join(s["citation"] for s in r["sources"]), "\n")
