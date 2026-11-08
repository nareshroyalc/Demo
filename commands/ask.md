---
description: Ask Brightline anything. Claude decides whether to use the policy documents, the database, or both.
argument-hint: <your question>
---

Answer this question using the **Brightline** connector tools: $ARGUMENTS

Plan before calling tools:
- Policy, rule, window, fee, SLA, discount or warranty question: follow the `docs-research` skill (`search_docs`).
- Numbers, counts, rankings or lists about customers, orders, shipments or tickets: follow the `sql-analyst` skill (`list_tables`, `describe_table`, `run_sql`).
- A rule applied to real orders or customers: follow the `docs-plus-data` skill (rule from documents first, facts from SQL second).

Cite documents as `[Title, p.N]`, state the SQL filters you used, and show key numbers in a small table. If the sources do not contain the answer, say so.
