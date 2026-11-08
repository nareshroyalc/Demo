---
name: docs-plus-data
description: Use when a question needs both a policy rule AND facts from the database, e.g. which orders qualify for late-delivery credit, which tickets breached priority rules, whether a discount exceeded policy caps.
---

# Docs plus data

Questions like "which late orders get compensation and how much?" mix a **rule** with **facts**. Work in this order:

1. **Rule first.** Use `search_docs` to retrieve the exact rule: thresholds, percentages, windows, tier exceptions (for example the SLA table, the late-compensation table, Platinum differences).
2. **Facts second.** Use `list_tables`/`describe_table`, then `run_sql` to find the rows the rule applies to. Encode the rule's thresholds in the query (for example `CASE WHEN days_late BETWEEN 1 AND 2 THEN 5 ...`).
3. **Combine.** Apply the rule to each row/group. Compute the money amounts in SQL when possible so the numbers are auditable.
4. **Answer in three parts:** (a) the rule with citation, (b) the matching data as a short table, (c) the conclusion (counts, totals, exceptions). Mention any assumption and any rule you could not confirm.

Never invent a threshold. If the document does not state it, say so and ask the user.
