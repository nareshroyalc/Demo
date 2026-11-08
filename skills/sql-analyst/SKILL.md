---
name: sql-analyst
description: Use when the user asks for numbers, counts, rankings, trends or lists about customers, orders, products, shipments or support tickets from the operational database.
---

# SQL analyst

1. Call `list_tables`, then `describe_table` for each table you need. Never guess column names.
2. Write ONE read-only SELECT. Prefer explicit JOINs; aggregate in SQL rather than fetching raw rows.
3. Revenue = `SUM(order_items.quantity * order_items.unit_price * (1 - order_items.discount_pct/100.0))`. Exclude orders with status `Cancelled` unless asked.
4. Dates are ISO text. Use `date()`, `strftime('%Y-%m', col)` and `julianday()` for date math. Today's date in this dataset is 2026-11-08.
5. Late delivery: `shipments.transit_business_days - shipments.sla_days` = business days late (positive means late; NULL transit means not yet delivered). Use these columns directly; do not recompute from dates.
6. State the exact filters used (date range, statuses) in the answer, and show the key numbers in a small table.
7. If `run_sql` returns an error, read it, fix the query once or twice, then explain what failed.
