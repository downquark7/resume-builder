from __future__ import annotations
from pathlib import Path
from typing import Dict


def load_data_dir(data_dir: str | Path) -> Dict[str, str]:
    """Load all .txt files in data_dir as {basename_without_ext: text}."""
    p = Path(data_dir)
    result: Dict[str, str] = {}
    if not p.exists():
        return result
    for f in p.glob("*.txt"):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = f.read_text(errors="ignore")
        result[f.stem] = text.strip()
    return result
