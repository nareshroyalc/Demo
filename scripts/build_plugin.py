"""Package the Claude plugin as dist/brightline-plugin.zip (plugin files at the zip root).

Contents: .claude-plugin/plugin.json, skills/ (single source shared with the built-in agent), commands/.
Deliberately NOT included: .mcp.json, URLs or tokens. The plugin relies on the 'Brightline' connector that
is already added in Claude, so the zip contains no secrets and is safe to share.

Run:  python scripts/build_plugin.py
"""
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "brightline-plugin.zip"

manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
files = [ROOT / ".claude-plugin" / "plugin.json"]
files += sorted((ROOT / "skills").glob("*/SKILL.md"))
files += sorted((ROOT / "commands").glob("*.md"))
files.append(ROOT / "PLUGIN_README.md")

OUT.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, f.relative_to(ROOT).as_posix())

print(f"{manifest['name']} v{manifest['version']} -> {OUT}")
with zipfile.ZipFile(OUT) as z:
    for i in z.infolist():
        print(f"  {i.filename}  ({i.file_size} B)")
