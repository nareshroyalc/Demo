"""Central configuration. Reads .env once; everything else imports from here."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DOCS_DIR = ROOT / "data" / "docs"
DB_PATH = ROOT / "data" / "demo.db"
QDRANT_PATH = ROOT / "data" / "qdrant"
SKILLS_DIR = ROOT / "skills"
UI_DIR = ROOT / "ui"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.1-flash-lite")
EMBED_DIM = 768

MCP_TOKEN = os.getenv("MCP_TOKEN", "").strip()  # bearer token for /mcp (unset = open, local dev only)
APP_PASSWORD = os.getenv("APP_PASSWORD", "").strip()  # HTTP Basic password for UI, /agent and /api (unset = open)
AGENT_ENGINE = os.getenv("AGENT_ENGINE", "langgraph").strip().lower()  # "langgraph" or "plain" (hand-written loop)
PROMPT_CACHE = os.getenv("PROMPT_CACHE", "auto").strip().lower()  # "auto" (try, fall back silently) or "off"
PROMPT_CACHE_TTL_SECONDS = int(os.getenv("PROMPT_CACHE_TTL_SECONDS", "3600"))
AGENT_RATE_PER_MIN = int(os.getenv("AGENT_RATE_PER_MIN", "8"))  # per client IP

COLLECTION = "brightline_docs"
CHUNK_CHARS = 900
CHUNK_OVERLAP = 150
SQL_MAX_ROWS = 200
