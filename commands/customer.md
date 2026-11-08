---
description: One-page customer summary from Brightline data (tier, revenue, late deliveries, tickets) plus the policies that apply to that tier.
argument-hint: <customer name, e.g. "Zenith Associates">
---

Build a customer summary for **$ARGUMENTS** using the **Brightline** connector tools.

1. `describe_table` for `customers`, `orders`, `order_items`, `shipments`, `support_tickets`, then find the customer by name (use `LIKE` and say if several match).
2. With `run_sql`, collect: region, tier, joined date; order count and revenue (`quantity * unit_price * (1 - discount_pct/100.0)`, excluding cancelled); number of late deliveries and the worst delay; support tickets by issue type and priority.
3. With `search_docs`, find what applies to that tier: return window, restocking fee, SLA days for their region, additional discount.
4. Reply with a short profile table, then 3 bullet insights (for example unresolved tickets, credits owed for late deliveries, tier-upgrade potential), citing documents as `[Title, p.N]`.
