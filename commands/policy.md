---
description: Look up a Brightline policy and quote it with citations (returns, shipping SLA, pricing, support, warranty).
argument-hint: <topic, e.g. "refund window for Platinum customers">
---

Look up this policy topic in the **Brightline** documents: $ARGUMENTS

Follow the `docs-research` skill: run `search_docs`, read neighbouring pages with `get_document_page` if a table or clause is cut off, and follow cross-references to other policies. Reply with the rule first, then conditions and exceptions, quoting numbers exactly and citing every claim as `[Title, p.N]`. Do not query the database. If the documents do not cover the topic, say so.
