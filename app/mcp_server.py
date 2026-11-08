"""The /mcp endpoint: RETRIEVAL ONLY. No LLM runs here; the calling agent (Claude, etc.) writes the answer.

Tool descriptions are the API contract the calling model reads, so they say when to use each tool.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.types import ToolAnnotations

from . import retrieval

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

mcp = FastMCP(
    "brightline-retrieval",
    instructions=(
        "Retrieval tools for Brightline Supplies (a fictional B2B office-supplies company). "
        "POLICY DOCUMENTS (returns, shipping SLA, pricing, support, warranty) are searched with search_docs. "
        "OPERATIONAL DATA (customers, orders, shipments, tickets) is queried with run_sql after checking the schema. "
        "Questions mixing a rule and facts about orders need BOTH: look up the rule in documents, then compute facts in SQL. "
        "Always cite documents as returned in 'citation'. These tools only retrieve data; compose the answer yourself."
    ),
    streamable_http_path="/mcp",
    json_response=True,
    stateless_http=True,
    # The library only trusts the Host header "localhost" by default, which would reject
    # https://<name>.onrender.com. Access is controlled by the bearer token (MCP_TOKEN) instead.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.tool(annotations=READ_ONLY)
def search_docs(query: str, k: int = 5, doc: str | None = None) -> dict:
    """Search the company policy PDFs (returns & refunds, shipping SLA & late compensation, pricing & discounts,
    support handbook, product catalog & warranty). Use for any question about rules, policies, windows, fees,
    SLAs, thresholds or warranty terms. Returns the best passages with a 'citation' for each.

    Args:
        query: What to look for, in natural language (include key terms like 'Platinum', 'damaged', 'SLA').
        k: Number of passages to return (1-10, default 5).
        doc: Optional filename fragment to restrict search, e.g. 'shipping'.
    """
    return {"results": retrieval.search_docs(query, k, doc)}


@mcp.tool(annotations=READ_ONLY)
def list_documents() -> dict:
    """List the available policy documents with page and passage counts. Use to see what is searchable."""
    return {"documents": retrieval.list_documents()}


@mcp.tool(annotations=READ_ONLY)
def get_document_page(doc: str, page: int) -> dict:
    """Read the full text of one page of a policy document, when a search hit needs more surrounding context.

    Args:
        doc: Filename exactly as returned by list_documents / search_docs, e.g. '02_shipping_and_delivery_sla.pdf'.
        page: 1-based page number.
    """
    return retrieval.get_document_page(doc, page)


@mcp.tool(annotations=READ_ONLY)
def list_tables() -> dict:
    """List the tables in the Brightline operational database (SQLite) with row counts. Start here for data questions."""
    return {"tables": retrieval.list_tables()}


@mcp.tool(annotations=READ_ONLY)
def describe_table(table: str, sample_rows: int = 3) -> dict:
    """Show a table's columns, types, foreign keys and a few sample rows. Call before writing SQL against a table.

    Args:
        table: Table name from list_tables.
        sample_rows: How many example rows to include (0-5).
    """
    return retrieval.describe_table(table, sample_rows)


@mcp.tool(annotations=READ_ONLY)
def run_sql(sql: str, max_rows: int = 50) -> dict:
    """Run ONE read-only SQLite SELECT (or WITH ... SELECT) against the operational database.
    Writes are rejected. Max 200 rows, 5 s timeout. Dates are ISO text (YYYY-MM-DD); use julianday()/date() for math.
    Business days late = shipments.transit_business_days - shipments.sla_days (positive = late; NULL = not delivered yet).

    Args:
        sql: A single SELECT statement.
        max_rows: Row cap (default 50, max 200).
    """
    return retrieval.run_sql(sql, max_rows)
