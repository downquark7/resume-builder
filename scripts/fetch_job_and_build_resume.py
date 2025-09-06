from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, List
from resume_builder.io.job_fetcher import fetch_job_text
from resume_builder.io.data_loader import load_data_dir
from resume_builder.chains.tailor_resume import tailor_resume_json
from resume_builder.render.pdf import render_resume_pdf
from resume_builder.config import settings


def _normalize_list_field(value: Any) -> List[str]:
    """Coerce a field into a list of strings for rendering.
    - If value is a JSON-encoded string (e.g., '["A", "B"]' or '{...}') try to json.loads it.
    - If value is a dict, convert items into readable strings.
    - If value is a list of dicts/objects, stringify each item sensibly.
    - If value is a plain string, wrap it into a single-item list if non-empty; otherwise return [].
    - If value is None or empty, return [].
    """
    def to_str(x: Any) -> str:
        if isinstance(x, (str, int, float)):
            return str(x)
        if isinstance(x, dict):
            # Try common keys, else a compact JSON
            for k in ("title", "company", "role", "name", "text", "description"):
                if k in x and isinstance(x[k], (str, int, float)):
                    return str(x[k])
            return json.dumps(x, ensure_ascii=False)
        return json.dumps(x, ensure_ascii=False)

    if value is None:
        return []

    # If it's a JSON-like string, parse it
    if isinstance(value, str):
        s = value.strip()
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("{") and s.endswith("}")):
            try:
                value = json.loads(s)
            except Exception:
                # Not valid JSON; keep as string
                pass
        else:
            return [s] if s else []

    if isinstance(value, dict):
        # Convert dict to a list with a single readable string
        return [to_str(value)]

    if isinstance(value, list):
        items: List[str] = []
        for item in value:
            if isinstance(item, list):
                # Flatten one level
                items.extend([to_str(x) for x in item])
            else:
                items.append(to_str(item))
        # Filter empty strings
        return [x for x in items if x and x.strip()]

    # Fallback: stringify
    return [to_str(value)]


def main():
    ap = argparse.ArgumentParser(description="Fetch job URL and build tailored resume PDF")
    ap.add_argument("--url", required=True, help="Job posting URL")
    ap.add_argument("--data-dir", default="./data", help="Path to data directory of .txt files")
    ap.add_argument("--out", default="./resume.pdf", help="Output PDF or HTML path")
    ap.add_argument("--model", default=settings.ollama_model)
    ap.add_argument("--temperature", type=float, default=settings.llm_temperature)
    args = ap.parse_args()

    job = fetch_job_text(args.url)
    sources = load_data_dir(args.data_dir)

    print("Fetched job text length:", len(job))
    print("Loaded sources:", list(sources.keys()))

    tailored = tailor_resume_json(job, sources, model=args.model, temperature=args.temperature)

    # Normalize structure for renderer, parsing JSON-like strings into lists
    summary = tailored.get("summary", "")
    skills = _normalize_list_field(tailored.get("skills", []))
    experience = _normalize_list_field(tailored.get("experience", []))
    projects = _normalize_list_field(tailored.get("projects", []))
    education = _normalize_list_field(tailored.get("education", []))
    extras = _normalize_list_field(tailored.get("extras", []))

    data = {
        "name": sources.get("name", ""),
        "summary": summary if isinstance(summary, str) else json.dumps(summary, ensure_ascii=False),
        "skills": skills,
        "experience": experience,
        "projects": projects,
        "education": education,
        "extras": extras,
        # Enable LLM-driven final layout: ordering, counts, and project slimming
        "llm_render": True,
    }

    out_path = render_resume_pdf(data, args.out)
    print("Wrote:", out_path)

    # Also save the raw JSON next to the PDF for inspection
    json_path = Path(args.out).with_suffix(".json")
    json_path.write_text(json.dumps(tailored, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved structured JSON:", json_path)


if __name__ == "__main__":
    main()
