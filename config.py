"""Central configuration. Loads .env and exposes settings used across the app."""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "").strip()

# Fast model for the parallel research agents; pro model for risk + report reasoning.
FAST_MODEL = os.getenv("GEMINI_FAST_MODEL", "gemini-2.5-flash").strip()
PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro").strip()

# "tavily" if a key is present, else free keyless "duckduckgo".
SEARCH_BACKEND = "tavily" if TAVILY_API_KEY else "duckduckgo"

# Max characters of fetched page text handed to the LLM (rough token budget).
MAX_PAGE_CHARS = int(os.getenv("MAX_PAGE_CHARS", "6000"))


def require_api_key() -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return GEMINI_API_KEY
