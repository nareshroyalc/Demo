"""Show the demo database in the terminal (read-only), for presentations.

  python scripts/show_data.py             list the demo queries
  python scripts/show_data.py 3           run demo query number 3
  python scripts/show_data.py all         run every demo query
  python scripts/show_data.py "SELECT ..."  run your own single SELECT

The database is opened read-only, so nothing can be changed.
"""
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "demo.db"

DEMO = [
    ("Which tables exist?",
     "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"),
    ("What does a row look like?",
     "SELECT * FROM customers LIMIT 5"),
    ("How many Platinum customers?",
     "SELECT COUNT(*) AS platinum_customers\nFROM customers\nWHERE tier = 'Platinum'"),
    ("Customers per tier",
     "SELECT tier, COUNT(*) AS customers\nFROM customers\nGROUP BY tier\nORDER BY customers DESC"),
    ("Orders by status",
     "SELECT status, COUNT(*) AS orders\nFROM orders\nGROUP BY status\nORDER BY orders DESC"),
    ("Busiest customers (a join)",
     "SELECT c.name, c.tier, COUNT(*) AS orders\nFROM orders o\nJOIN customers c ON c.customer_id = o.customer_id\n"
     "GROUP BY c.customer_id\nORDER BY orders DESC\nLIMIT 3"),
    ("Top revenue, cancelled orders left out",
     "SELECT c.name,\n       ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct/100.0)), 2) AS revenue\n"
     "FROM customers c\nJOIN orders o       ON o.customer_id = c.customer_id\nJOIN order_items oi ON oi.order_id = o.order_id\n"
     "WHERE o.status <> 'Cancelled'\nGROUP BY c.customer_id\nORDER BY revenue DESC\nLIMIT 3"),
]


def _is_number(v: str) -> bool:
    try:
        float(v.replace(",", ""))
        return True
    except ValueError:
        return False


def run(sql: str) -> None:
    first = sql.strip().split(None, 1)[0].upper() if sql.strip() else ""
    if first not in ("SELECT", "WITH") or ";" in sql.strip().rstrip(";"):
        sys.exit("Only a single SELECT query is allowed.")
    db = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    cur = db.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cells = [[("" if v is None else f"{v:,.2f}" if isinstance(v, float) else str(v)) for v in r] for r in rows]
    widths = [max(len(c), *(len(r[i]) for r in cells)) if cells else len(c) for i, c in enumerate(cols)]
    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    print(line)
    print("| " + " | ".join(c.ljust(w) for c, w in zip(cols, widths)) + " |")
    print(line)
    for r in cells:
        print("| " + " | ".join(v.rjust(w) if _is_number(v) else v.ljust(w)
                               for v, w in zip(r, widths)) + " |")
    print(line)
    print(f"{len(rows)} row{'s' if len(rows) != 1 else ''}")


def show_demo(n: int) -> None:
    title, sql = DEMO[n - 1]
    print(f"\n=== {n}. {title} ===\n")
    print(sql + ";\n")
    run(sql)


def main() -> None:
    if not DB.exists():
        sys.exit(f"Database not found: {DB}")
    arg = " ".join(sys.argv[1:]).strip()
    if not arg:
        print("Demo queries (python scripts/show_data.py <number>):\n")
        for i, (title, _) in enumerate(DEMO, 1):
            print(f"  {i}. {title}")
        print("\n  all   run every demo query\n  \"SELECT ...\"   run your own query")
    elif arg.lower() == "all":
        for i in range(1, len(DEMO) + 1):
            show_demo(i)
    elif arg.isdigit() and 1 <= int(arg) <= len(DEMO):
        show_demo(int(arg))
    else:
        print(arg + "\n")
        run(arg)


if __name__ == "__main__":
    main()
