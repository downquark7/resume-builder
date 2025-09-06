from __future__ import annotations
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent / "text"


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """
    Load a prompt text file from prompts/text directory by stem name.
    Example names: 'tailoring_system', 'tailoring_human', 'review_system', 'review_human'.
    """
    path = BASE_DIR / f"{name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")
