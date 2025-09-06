from __future__ import annotations
import argparse
import json
from pathlib import Path
from resume_builder.io.job_fetcher import fetch_job_text
from resume_builder.io.data_loader import load_data_dir
from resume_builder.chains.tailor_resume import tailor_resume_json
from resume_builder.render.pdf import render_resume_pdf
from resume_builder.config import settings


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

    # Normalize structure for renderer
    data = {
        "name": sources.get("name", ""),
        "summary": tailored.get("summary", ""),
        "skills": tailored.get("skills", []),
        "experience": tailored.get("experience", []),
        "projects": tailored.get("projects", []),
        "education": tailored.get("education", []),
        "extras": tailored.get("extras", []),
    }

    out_path = render_resume_pdf(data, args.out)
    print("Wrote:", out_path)

    # Also save the raw JSON next to the PDF for inspection
    json_path = Path(args.out).with_suffix(".json")
    json_path.write_text(json.dumps(tailored, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Saved structured JSON:", json_path)


if __name__ == "__main__":
    main()
