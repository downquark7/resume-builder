# Live system script: run end-to-end checks with optional Ollama model.
# This script is intended to be executed manually, not collected by pytest.

from __future__ import annotations
import sys
from pathlib import Path
import json
import socket
import argparse
import time

from resume_builder.config import settings
from resume_builder.llm.ollama_client import get_ollama_chat

LIVE_MODEL = "gemma3:4b-it-q8_0"
# LIVE_MODEL = "gpt-oss"

def _ollama_up(model: str, timeout: float = 2.0) -> bool:
    try:
        host, port = settings.ollama_base_url.replace("http://", "").replace("https://", "").split(":", 1)
        with socket.create_connection((host, int(port)), timeout=timeout):
            pass
    except Exception:
        return False
    try:
        chat = get_ollama_chat(model=model)
        ping_prompt = "ping: reply with pong"
        print(f"[llm] model={model} prompt (truncated 1000 chars):\n{ping_prompt[:1000]}\n--- end prompt ---")
        res = chat.invoke(ping_prompt)
        txt = res.content if hasattr(res, "content") else str(res)
        return "pong" in txt.lower() or len(txt.strip()) > 0
    except Exception:
        return False


def _judge_with_llm(prompt: str, model: str) -> str:
    # Log the prompt right before calling the LLM for transparency/debugging
    print(f"[llm] model={model} prompt (truncated 1000 chars):\n{prompt[:1000]}\n--- end prompt ---")
    chat = get_ollama_chat(model=model)
    res = chat.invoke(prompt)
    return res.content if hasattr(res, "content") else str(res)


def run_review_data_files(model: str, work_dir: Path, verbose: bool) -> bool:
    import scripts.review_data_files as mod
    out_md = work_dir / "suggestions.md"
    argv = [
        "prog",
        "--data-dir", str(Path("data").resolve()),
        "--out", str(out_md),
        "--model", model,
    ]
    if verbose:
        print("[review] argv:", " ".join(argv))
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv
    if not out_md.exists():
        print("[review] ERROR: suggestions.md not created at", out_md)
        return False
    content = out_md.read_text(encoding="utf-8")
    if verbose:
        print(f"[review] suggestions.md size: {len(content)} bytes")
    data_samples = []
    for f in Path("data").glob("*.txt"):
        if len(data_samples) >= 2:
            break
        try:
            data_samples.append((f.stem, f.read_text(encoding="utf-8", errors="ignore")[:1200]))
        except Exception:
            pass
    judge_prompt = (
        "You are grading whether a suggestions.md document contains concrete, helpful suggestions for improving resume source files.\n"
        "Consider the original file snippets and the suggestions document below.\n"
        "Return a single token: PASS if the suggestions contain at least some specific, actionable advice tied to the files; otherwise FAIL.\n\n"
        f"Original snippets: {json.dumps(dict(data_samples), ensure_ascii=False)[:2000]}\n\n"
        f"Suggestions.md content begins:\n{content[:4000]}\n\n"
        "Answer strictly with PASS or FAIL."
    )
    verdict = _judge_with_llm(judge_prompt, model=model).strip().upper()
    if verbose:
        print("[review] LLM verdict:", verdict)
    if not verdict.startswith("PASS"):
        print(f"[review] FAIL: LLM judge did not approve suggestions. Verdict: {verdict}")
        return False
    print("[review] PASS")
    return True


def run_check_library_activity(model: str, work_dir: Path, verbose: bool) -> bool:
    import scripts.check_library_activity as mod
    out_md = work_dir / "dependency_activity.md"
    argv = [
        "prog",
        "--requirements", str(Path("requirements.txt").resolve()),
        "--out", str(out_md),
    ]
    if verbose:
        print("[activity] argv:", " ".join(argv))
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv
    if not out_md.exists():
        print("[activity] ERROR: dependency_activity.md not created at", out_md)
        return False
    text = out_md.read_text(encoding="utf-8")
    if verbose:
        print(f"[activity] report size: {len(text)} bytes")
    judge_prompt = (
        "You are grading a dependency activity report generated from requirements.txt.\n"
        "It should list packages and discuss their recent activity (e.g., releases, commits, dates) and include a status judgment.\n"
        "Return PASS if it plausibly contains such information for multiple packages; otherwise FAIL.\n\n"
        f"Report content:\n{text[:4000]}\n\nAnswer strictly with PASS or FAIL."
    )
    verdict = _judge_with_llm(judge_prompt, model=model).strip().upper()
    if verbose:
        print("[activity] LLM verdict:", verdict)
    if not verdict.startswith("PASS"):
        print(f"[activity] FAIL: LLM judge did not approve dependency report. Verdict: {verdict}")
        return False
    print("[activity] PASS")
    return True


def run_fetch_job_and_build_resume(model: str, work_dir: Path, verbose: bool) -> bool:
    import scripts.fetch_job_and_build_resume as mod
    out_pdf = work_dir / "resume.pdf"
    argv = [
        "prog",
        "--url", "https://www.rfc-editor.org/rfc/rfc8259",
        "--data-dir", str(Path("data").resolve()),
        "--out", str(out_pdf),
        "--model", model,
    ]
    if verbose:
        print("[resume] argv:", " ".join(argv))
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv
    rendered = out_pdf if out_pdf.exists() else out_pdf.with_suffix(".html")
    if not rendered.exists():
        print("[resume] ERROR: expected rendered resume file at", rendered)
        return False
    json_sidecar = out_pdf.with_suffix(".json")
    if not json_sidecar.exists():
        print("[resume] ERROR: expected JSON sidecar at", json_sidecar)
        return False
    data = json.loads(json_sidecar.read_text(encoding="utf-8"))
    if verbose:
        print("[resume] JSON keys:", list(data.keys()))
    sources = {}
    for f in Path("data").glob("*.txt"):
        try:
            sources[f.stem] = f.read_text(encoding="utf-8", errors="ignore")[:1200]
        except Exception:
            pass
    judge_prompt = (
        "You are grading whether a structured resume JSON is a reasonable effort to tailor a resume to a role.\n"
        "The JSON should include keys like summary, skills, experience, projects, education, extras, with plausible content.\n"
        "Return PASS if the JSON appears coherent and tailored (even approximately) given the provided sources and a long target description; otherwise FAIL.\n\n"
        f"Sources (snippets): {json.dumps(sources, ensure_ascii=False)[:2000]}\n\n"
        f"Resume JSON: {json.dumps(data, ensure_ascii=False)[:3000]}\n\nAnswer strictly with PASS or FAIL."
    )
    verdict = _judge_with_llm(judge_prompt, model=model).strip().upper()
    if verbose:
        print("[resume] LLM verdict:", verdict)
    if not verdict.startswith("PASS"):
        print(f"[resume] FAIL: LLM judge did not approve tailored resume. Verdict: {verdict}")
        return False
    print("[resume] PASS")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run live system checks using local Ollama LLM.")
    parser.add_argument("--model", default=LIVE_MODEL, help="Ollama model to use (default: %(default)s)")
    parser.add_argument("--only", choices=["review", "activity", "resume"], help="Run only a single check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--work-dir", default=str(Path.cwd() / ".live_runs"), help="Working directory for outputs")
    args = parser.parse_args(argv)

    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    # Display environment debug
    host, port = None, None
    try:
        host, port = settings.ollama_base_url.replace("http://", "").replace("https://", "").split(":", 1)
    except Exception:
        pass
    print(f"[env] ollama_base_url={settings.ollama_base_url}")
    if host and port:
        print(f"[env] resolved host={host} port={port}")

    if not _ollama_up(args.model):
        print("[env] Ollama not available or model not responding; skipping checks.")
        return 0  # Treat as non-fatal skip when run as a script

    start = time.time()
    checks = []
    if args.only is None:
        checks = [
            ("review", run_review_data_files),
            ("activity", run_check_library_activity),
            ("resume", run_fetch_job_and_build_resume),
        ]
    else:
        mapping = {
            "review": run_review_data_files,
            "activity": run_check_library_activity,
            "resume": run_fetch_job_and_build_resume,
        }
        checks = [(args.only, mapping[args.only])]

    all_ok = True
    for name, func in checks:
        print(f"[run] Starting check: {name}")
        try:
            ok = func(args.model, work_dir, args.verbose)
        except Exception as e:
            ok = False
            print(f"[{name}] EXCEPTION: {type(e).__name__}: {e}")
        print(f"[run] Finished {name}: {'PASS' if ok else 'FAIL'}\n")
        all_ok = all_ok and ok

    elapsed = time.time() - start
    print(f"[done] Total elapsed: {elapsed:.1f}s. Overall status: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
