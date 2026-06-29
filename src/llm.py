"""Gemini LLM factory."""
from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI

import config


def get_llm(model: str | None = None, temperature: float = 0.2) -> ChatGoogleGenerativeAI:
    """Return a configured Gemini chat model.

    Defaults to the fast model. Pass config.PRO_MODEL for heavier reasoning.
    """
    return ChatGoogleGenerativeAI(
        model=model or config.FAST_MODEL,
        google_api_key=config.require_api_key(),
        temperature=temperature,
    )
