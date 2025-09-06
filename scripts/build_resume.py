from __future__ import annotations
import argparse
import shutil
import subprocess
from pathlib import Path

from resume_builder.chains.pipeline import run_rewrite, RewriteConfig
from resume_builder.config import settings


def main():
    ap = argparse.ArgumentParser(description="Build YAML resume (and optional PDF). You may provide a job description (URL/file/text) to tailor the resume, or omit it to build from your data only.")
    src = ap.add_mutually_exclusive_group(required=False)
    src.add_argument("--job-url", help="Job posting URL")
    src.add_argument("--job-file", help="Path to a local file containing the raw job posting text")
    src.add_argument("--job-text", help="Raw job posting text inline")

    ap.add_argument("--data-dir", default="./data", help="Path to data directory of .txt files")
    ap.add_argument("--model", default=settings.ollama_model)
    ap.add_argument("--temperature", type=float, default=settings.llm_temperature)
    ap.add_argument("--out", default="./resume.yaml", help="Output YAML resume path")
    ap.add_argument("--log-file", default=None, help="Optional path to append all LLM outputs for the rewrite run")
    ap.add_argument("--no-build-pdf", action="store_true", help="Skip calling 'yamlresume build' after writing YAML")

    args = ap.parse_args()

    job_text = None
    if args.job_file:
        job_text = Path(args.job_file).read_text(encoding="utf-8")
    elif args.job_text:
        job_text = args.job_text
    elif args.job_url:
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

    # Optionally build PDF via yamlresume
    if not args.no_build_pdf:
        yamlresume_bin = shutil.which("yamlresume")
        if yamlresume_bin is None:
            print("yamlresume CLI not found on PATH. Install it to build the PDF, or rerun with --no-build-pdf to skip.")
        else:
            try:
                print("Running:", yamlresume_bin, "build", str(out_path))
                subprocess.run([yamlresume_bin, "build", str(out_path)], check=True)
                print("PDF build completed.")
            except subprocess.CalledProcessError as e:
                print("yamlresume build failed with exit code", e.returncode)


if __name__ == "__main__":
    main()
