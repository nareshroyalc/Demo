"""Package the Claude plugin.

  python scripts/build_plugin.py                  -> dist/brightline-plugin.zip
        skills + commands only; no URL or token. Safe to share. Needs the 'Brightline' connector added separately.

  python scripts/build_plugin.py --with-connector -> dist/brightline-plugin-with-connector.zip
        also bundles .mcp.json with the connector URL read from BRIGHTLINE_MCP_URL (in .env or the environment),
        e.g. https://<service>.onrender.com/mcp?token=<MCP_TOKEN>.
        CONTAINS A SECRET: for your own use only. dist/ is git-ignored; never commit or share this zip.
"""
import json
import os
import sys
import zipfile
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
with_connector = "--with-connector" in sys.argv
OUT = ROOT / "dist" / ("brightline-plugin-with-connector.zip" if with_connector else "brightline-plugin.zip")

manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
files = [ROOT / ".claude-plugin" / "plugin.json"]
files += sorted((ROOT / "skills").glob("*/SKILL.md"))
files += sorted((ROOT / "commands").glob("*.md"))
files.append(ROOT / "PLUGIN_README.md")

mcp_json = None
if with_connector:
    url = os.getenv("BRIGHTLINE_MCP_URL", "").strip()
    if not url.startswith("https://") or "/mcp" not in url:
        sys.exit("Set BRIGHTLINE_MCP_URL (e.g. https://<service>.onrender.com/mcp?token=<MCP_TOKEN>) in .env")
    mcp_json = json.dumps({"mcpServers": {"brightline": {"type": "http", "url": url}}}, indent=2)

OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, f.relative_to(ROOT).as_posix())
    if mcp_json:
        z.writestr(".mcp.json", mcp_json)

print(f"{manifest['name']} v{manifest['version']} -> {OUT}")
with zipfile.ZipFile(OUT) as z:
    for i in z.infolist():
        print(f"  {i.filename}  ({i.file_size} B)")
if with_connector:
    print("\nWARNING: this zip contains your MCP token. Do not share it or commit it.")
