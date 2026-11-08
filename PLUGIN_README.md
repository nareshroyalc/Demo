# Brightline plugin

Skills and slash commands for the **Brightline** connector (policy PDFs + sales database).

**Requires:** the Brightline MCP connector added and enabled in Claude (it provides the tools
`search_docs`, `list_documents`, `get_document_page`, `list_tables`, `describe_table`, `run_sql`).

## Commands
- `/brightline:ask <question>` any question; Claude picks documents, database or both
- `/brightline:policy <topic>` quote a policy with citations
- `/brightline:late-orders [filter]` late deliveries and the credit owed per band
- `/brightline:customer <name>` customer summary plus the policies for their tier

## Skills (used automatically)
- `docs-research`: policy questions from the PDFs
- `sql-analyst`: numbers and lists from the database
- `docs-plus-data`: apply a policy rule to real orders or customers
