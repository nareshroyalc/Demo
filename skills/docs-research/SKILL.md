---
name: docs-research
description: Use when the user asks about Brightline policies, rules, windows, fees, SLAs, discounts, support procedures or warranty terms and the answer lives in the policy PDFs.
---

# Docs research

1. Call `search_docs` with a focused query. Include the specific terms from the question (tier name, category, "damaged", "late").
2. If the top passages are partial (a table cut off, a clause referencing another section), call `get_document_page` for that page, or run a second `search_docs` with the referenced topic.
3. Policies cross-reference each other (returns <-> shipping SLA <-> support). Follow cross-references before concluding.
4. Answer with the rule first, then conditions/exceptions. Quote numbers exactly (days, percentages, dollar limits).
5. Cite every claim as `[Title, p.N]` using the `citation` field. If the documents do not say, state that plainly instead of guessing.
