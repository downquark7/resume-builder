from __future__ import annotations
import argparse
from pathlib import Path

from resume_builder.chains.rewrite_pipeline import run_rewrite, RewriteConfig
from resume_builder.config import settings


def main():
    ap = argparse.ArgumentParser(description="Rewrite pipeline: fetch/clean job, shorten files, build YAML resume")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--job-url", help="Job posting URL")
    src.add_argument("--job-file", help="Path to a local file containing the raw job posting text")
    src.add_argument("--job-text", help="Raw job posting text inline")

    ap.add_argument("--data-dir", default="./data", help="Path to data directory of .txt files")
    ap.add_argument("--model", default=settings.ollama_model)
    ap.add_argument("--temperature", type=float, default=settings.llm_temperature)
    ap.add_argument("--out", default="./resume.yaml", help="Output YAML resume path")
    ap.add_argument("--log-file", default=None, help="Optional path to append all LLM outputs for the rewrite run")

    args = ap.parse_args()

    if args.job_file:
        job_text = Path(args.job_file).read_text(encoding="utf-8")
    elif args.job_text:
        job_text = args.job_text
    else:
        job_text = args.job_url

    # Determine log file path
    log_file = args.log_file
    if log_file is None and args.out:
        out_path_tmp = Path(args.out)
        log_file = str(out_path_tmp.with_suffix(out_path_tmp.suffix + ".llm.log"))

    cfg = RewriteConfig(model=args.model, temperature=args.temperature, log_file=log_file)
    yaml_doc = run_rewrite(job_text, args.data_dir, cfg)

    out_path = Path(args.out)
    out_path.write_text(yaml_doc, encoding="utf-8")
    print("Wrote:", out_path)


if __name__ == "__main__":
    main()
