from __future__ import annotations
from pathlib import Path
from typing import Dict


def load_data_dir(data_dir: str | Path) -> Dict[str, str]:
    """Load all .txt files in data_dir as {basename_without_ext: text}.

    Also normalizes a few common filename aliases so downstream chains can
    recognize the intended categories:
      - "work history" or "work_history" -> "experience"
      - "contact information" or "contact_information" -> "contact"
    """
    p = Path(data_dir)
    result: Dict[str, str] = {}
    if not p.exists():
        return result

    alias_map = {
        "work history": "experience",
        "work_history": "experience",
        "contact information": "contact",
        "contact_information": "contact",
    }

    for f in p.glob("*.txt"):
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = f.read_text(errors="ignore")
        key = f.stem.strip()
        key_lower = key.lower()
        norm_key = alias_map.get(key_lower, key)
        # If both alias and canonical exist, prefer canonical without overwrite
        if norm_key in result and norm_key != key:
            # Append non-duplicate content
            existing = result[norm_key]
            new_text = text.strip()
            if new_text and new_text not in existing:
                result[norm_key] = (existing + "\n\n" + new_text).strip()
        else:
            result[norm_key] = text.strip()
    return result
