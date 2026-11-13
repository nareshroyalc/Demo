"""Show the demo database in the terminal (read-only), for presentations.

  python scripts/show_data.py tables      every table: name, row count, column names
  python scripts/show_data.py tables customers   one table: its columns and 5 sample rows
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


def print_table(cols: list[str], cells: list[list[str]], footer: str | None = None) -> None:
    """Print a boxed text table. Numbers are right-aligned, text is left-aligned."""
    widths = [max(len(c), *(len(r[i]) for r in cells)) if cells else len(c) for i, c in enumerate(cols)]
    line = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    print(line)
    print("| " + " | ".join(c.ljust(w) for c, w in zip(cols, widths)) + " |")
    print(line)
    for r in cells:
        print("| " + " | ".join(v.rjust(w) if _is_number(v) else v.ljust(w) for v, w in zip(r, widths)) + " |")
    print(line)
    if footer:
        print(footer)


def _fmt(v) -> str:
    return "" if v is None else f"{v:,.2f}" if isinstance(v, float) else str(v)


def run(sql: str) -> None:
    first = sql.strip().split(None, 1)[0].upper() if sql.strip() else ""
    if first not in ("SELECT", "WITH") or ";" in sql.strip().rstrip(";"):
        sys.exit("Only a single SELECT query is allowed.")
    db = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    cur = db.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    print_table(cols, [[_fmt(v) for v in r] for r in rows], f"{len(rows)} row{'s' if len(rows) != 1 else ''}")


def _table_names(db: sqlite3.Connection) -> list[str]:
    return [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]


def _wrap(items: list[str], width: int = 58) -> list[str]:
    """Join names with commas and wrap them into lines of at most `width` characters."""
    lines, cur = [], ""
    for i, name in enumerate(items):
        piece = name + ("," if i < len(items) - 1 else "")
        if cur and len(cur) + 1 + len(piece) > width:
            lines.append(cur)
            cur = piece
        else:
            cur = f"{cur} {piece}".strip()
    if cur:
        lines.append(cur)
    return lines


def show_tables(name: str | None = None) -> None:
    db = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    names = _table_names(db)
    if name is None:
        cells = []
        for t in names:
            n = db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            cols = [r[1] for r in db.execute(f'PRAGMA table_info("{t}")')]
            wrapped = _wrap(cols)
            cells.append([t, f"{n:,}", str(len(cols)), wrapped[0]])
            cells.extend(["", "", "", extra] for extra in wrapped[1:])
        print(f"\nDatabase: {DB.name}   ({len(names)} tables)\n")
        print_table(["Table", "Rows", "Cols", "Column names"], cells)
        return
    if name not in names:
        sys.exit(f"No table named '{name}'. Tables: {', '.join(names)}")
    n = db.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
    print(f"\nTable: {name}   ({n:,} rows)\n")
    schema = [[col, typ, "primary key" if pk else ""] for _cid, col, typ, _nn, _d, pk in db.execute(f'PRAGMA table_info("{name}")')]
    print_table(["Column", "Type", "Key"], schema)
    print("\nFirst 5 rows:\n")
    run(f'SELECT * FROM "{name}" LIMIT 5')


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
    elif arg.lower().split()[0] == "tables":
        parts = arg.split()
        show_tables(parts[1] if len(parts) > 1 else None)
    elif arg.lower() == "all":
        for i in range(1, len(DEMO) + 1):
            show_demo(i)
    elif arg.isdigit() and 1 <= int(arg) <= len(DEMO):
        show_demo(int(arg))
    elif arg.isdigit():
        sys.exit(f"Pick a number from 1 to {len(DEMO)}, or run the script with no arguments to see the list.")
    else:
        print(arg + "\n")
        run(arg)


if __name__ == "__main__":
    main()
