"""Minimal Gemini connectivity check. Run this first: `python check_key.py`."""
from src.llm import get_llm


def main() -> None:
    llm = get_llm()
    resp = llm.invoke("Reply with exactly the word: OK")
    print("Model replied:", repr(resp.content))


if __name__ == "__main__":
    main()
