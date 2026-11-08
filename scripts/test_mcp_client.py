"""Connect to the running server's /mcp endpoint with a real MCP client, list tools, call a few."""
import asyncio
import json
import os
import sys

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
TOKEN = os.getenv("MCP_TOKEN", "")


async def main() -> int:
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    async with streamablehttp_client(URL, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = (await s.list_tools()).tools
            print("TOOLS:", [t.name for t in tools])
            ok = True
            for name, args in [
                ("list_tables", {}),
                ("search_docs", {"query": "late delivery compensation percentage", "k": 2}),
                ("run_sql", {"sql": "SELECT COUNT(*) AS late FROM shipments WHERE transit_business_days > sla_days"}),
                ("run_sql", {"sql": "DELETE FROM orders"}),
            ]:
                res = await s.call_tool(name, args)
                text = res.content[0].text if res.content else ""
                print(f"\n{name}({json.dumps(args)[:70]}) isError={res.isError}\n  {" ".join(text.split())[:230]}")
            return 0 if ok else 1


sys.exit(asyncio.run(main()))
