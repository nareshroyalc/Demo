---
description: Report late deliveries and the compensation credit each one is owed under the Shipping SLA policy.
argument-hint: [optional filter, e.g. "Platinum customers" or "region West" or "last quarter"]
---

Produce a late-delivery compensation report using the **Brightline** connector tools. Optional filter: $ARGUMENTS

Follow the `docs-plus-data` skill:
1. `search_docs` for the late-delivery compensation table in the Shipping & Delivery SLA. Use the exact bands and percentages from the document; do not assume them.
2. `describe_table` for `shipments`, `orders`, `order_items`, `customers`. Late means `transit_business_days - sla_days > 0`. Only delivered shipments (`delivered_date` not null) count.
3. With one `run_sql` query, group late shipments by band and compute order value (`quantity * unit_price * (1 - discount_pct/100.0)`, excluding cancelled orders) and the credit owed per band.
4. Reply with: the rule and its citation, a table (band, orders, order value, credit owed), the total credit, and the 5 worst cases (customer, tier, days late). Apply the optional filter if one was given and say how you applied it.
