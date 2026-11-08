"""Quick check of the retrieval layer (works without a Gemini key: keyword search only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import ingest, retrieval  # noqa: E402

print("ingest:", ingest.ingest())
print("\n-- search_docs('refund window for damaged items')")
for r in retrieval.search_docs("refund window for damaged items", 3):
    print(f"  [{r['score']}] {r['citation']}: {r['text'][:90]!r}")
print("\n-- list_documents:", [d["doc"] for d in retrieval.list_documents()])
print("-- tables:", retrieval.list_tables())
print("-- sql:", retrieval.run_sql("SELECT tier, COUNT(*) n FROM customers GROUP BY tier"))
for bad in ["DROP TABLE customers", "SELECT 1; DELETE FROM orders", "pragma table_info(orders)", "UPDATE orders SET status='x'"]:
    print("-- blocked:", bad, "->", retrieval.run_sql(bad).get("error"))
