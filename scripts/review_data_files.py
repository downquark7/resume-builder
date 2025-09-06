from __future__ import annotations
import argparse
from pathlib import Path
from resume_builder.io.data_loader import load_data_dir
from resume_builder.chains.review_file import review_source_file
from resume_builder.config import settings


def main():
    ap = argparse.ArgumentParser(description="Review each file in data dir and suggest improvements")
    ap.add_argument("--data-dir", default="./data")
    ap.add_argument("--out", default="suggestions.md")
    ap.add_argument("--model", default=settings.ollama_model)
    ap.add_argument("--temperature", type=float, default=settings.llm_temperature)
    args = ap.parse_args()

    sources = load_data_dir(args.data_dir)

    lines = ["# Suggestions\n"]
    for name, content in sources.items():
        print(f"Reviewing {name}...")
        suggestion = review_source_file(name, content, model=args.model, temperature=args.temperature)
        lines.append(f"\n## {name}\n\n")
        lines.append(suggestion)
        lines.append("\n")

    out_path = Path(args.out)
    out_path.write_text("".join(lines), encoding="utf-8")
    print("Wrote suggestions:", out_path)


if __name__ == "__main__":
    main()
