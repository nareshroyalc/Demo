"""Call /agent/stream and show WHEN each event arrives (proves it streams, not buffers).

Run (server must be running):  python scripts/test_stream.py [question] [persona]
"""
import json
import sys
import time
import urllib.request

URL = "http://127.0.0.1:8010/agent/stream"
q = sys.argv[1] if len(sys.argv) > 1 else "What is the refund window for damaged items?"
persona = sys.argv[2] if len(sys.argv) > 2 else None

req = urllib.request.Request(URL, json.dumps({"question": q, "persona": persona}).encode(), {"Content-Type": "application/json"})
t0 = time.time()
resp = urllib.request.urlopen(req, timeout=180)
print("HTTP", resp.status, resp.headers.get("Content-Type"))
print("Q:", q)

events, buf, token_chars = [], "", 0
first = {}
for raw in resp:                                   # reads line by line as the server sends them
    line = raw.decode("utf-8").rstrip("\n")
    if not line.startswith("data: "):
        continue
    ev = json.loads(line[6:])
    t = time.time() - t0
    events.append((t, ev))
    kind = ev["type"]
    first.setdefault(kind, t)
    if kind == "token":
        token_chars += len(ev["text"])
        buf += ev["text"]
        continue
    if buf:
        print(f"  {events[-2][0]:5.1f}s  token x{sum(1 for _, e in events if e['type']=='token')} ({token_chars} chars so far)")
        buf = ""
    detail = {k: v for k, v in ev.items() if k not in ("type", "answer", "steps", "sources")}
    if kind == "done":
        detail = {"answer_chars": len(ev.get("answer", "")), "steps": len(ev.get("steps", [])), "usage": ev.get("usage")}
    print(f"  {t:5.1f}s  {kind:7} {json.dumps(detail, default=str)[:150]}")

kinds = [e["type"] for _, e in events]
n_tokens = kinds.count("token")
print(f"\nevents: {len(events)}  | token events: {n_tokens}  | first step at {first.get('step', float('nan')):.1f}s, "
      f"first token at {first.get('token', float('nan')):.1f}s, done at {first.get('done', float('nan')):.1f}s")
ok = kinds[0] == "start" and kinds[-1] == "done"
print("order ok (start ... done):", ok)
sys.exit(0 if ok else 1)
