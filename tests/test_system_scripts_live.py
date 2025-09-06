from __future__ import annotations
import os
import sys
from pathlib import Path
import json
import socket
import time

import pytest

from resume_builder.config import settings
from resume_builder.llm.ollama_client import get_ollama_chat


def _ollama_up(model: str, timeout: float = 2.0) -> bool:
    # Quick TCP check before a tiny LLM call to avoid long hangs.
    try:
        host, port = settings.ollama_base_url.replace("http://", "").replace("https://", "").split(":", 1)
        with socket.create_connection((host, int(port)), timeout=timeout):
            pass
    except Exception:
        return False
    # Minimal LLM probe
    try:
        chat = get_ollama_chat(model=model)
        res = chat.invoke("ping: reply with pong")
        txt = res.content if hasattr(res, "content") else str(res)
        return "pong" in txt.lower() or len(txt.strip()) > 0
    except Exception:
        return False


def _judge_with_llm(prompt: str, model: str) -> str:
    chat = get_ollama_chat(model=model)
    res = chat.invoke(prompt)
    return res.content if hasattr(res, "content") else str(res)
def test_review_data_files_live(tmp_path: Path, ollama_model: str):
    # Use the real script and the live data folder
    import scripts.review_data_files as mod

    if not _ollama_up(ollama_model):
        pytest.skip("Ollama not available or model not responding")

    out_md = tmp_path / "suggestions.md"
    argv = [
        "prog",
        "--data-dir", str(Path("data").resolve()),
        "--out", str(out_md),
        "--model", ollama_model,
    ]
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv

    assert out_md.exists()
    content = out_md.read_text(encoding="utf-8")

    # Ask the LLM to judge whether the suggestions look specific/actionable for at least one file
    data_samples = []
    # Load some originals to give the judge context
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
    verdict = _judge_with_llm(judge_prompt, model=ollama_model).strip().upper()
    assert verdict.startswith("PASS"), f"LLM judge did not approve suggestions. Verdict: {verdict}"


def test_check_library_activity_live(tmp_path: Path, ollama_model: str):
    # Generate dependency activity report from live requirements
    import scripts.check_library_activity as mod

    if not _ollama_up(ollama_model):
        pytest.skip("Ollama not available or model not responding")

    out_md = tmp_path / "dependency_activity.md"
    argv = [
        "prog",
        "--requirements", str(Path("requirements.txt").resolve()),
        "--out", str(out_md),
    ]
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv

    assert out_md.exists()
    text = out_md.read_text(encoding="utf-8")

    # LLM judge: Does this look like a reasonable dependency activity report (mentions packages and recency/status)?
    judge_prompt = (
        "You are grading a dependency activity report generated from requirements.txt.\n"
        "It should list packages and discuss their recent activity (e.g., releases, commits, dates) and include a status judgment.\n"
        "Return PASS if it plausibly contains such information for multiple packages; otherwise FAIL.\n\n"
        f"Report content:\n{text[:4000]}\n\nAnswer strictly with PASS or FAIL."
    )
    verdict = _judge_with_llm(judge_prompt, model=ollama_model).strip().upper()
    assert verdict.startswith("PASS"), f"LLM judge did not approve dependency report. Verdict: {verdict}"


def test_fetch_job_and_build_resume_live(tmp_path: Path, ollama_model: str):
    # Use a stable, long public page as a stand-in for a job description to avoid flakiness.
    # Even if it's not a job page, the system should still tailor and render.
    import scripts.fetch_job_and_build_resume as mod

    if not _ollama_up(ollama_model):
        pytest.skip("Ollama not available or model not responding")

    out_pdf = tmp_path / "resume.pdf"
    argv = [
        "prog",
        "--url", "https://www.rfc-editor.org/rfc/rfc8259",  # long, stable JSON RFC page
        "--data-dir", str(Path("data").resolve()),
        "--out", str(out_pdf),
        "--model", ollama_model,
    ]
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv

    # Either PDF or HTML may be produced depending on renderer
    rendered = out_pdf if out_pdf.exists() else out_pdf.with_suffix(".html")
    assert rendered.exists(), "Expected rendered resume file"

    json_sidecar = out_pdf.with_suffix(".json")
    assert json_sidecar.exists(), "Expected structured JSON sidecar"
    data = json.loads(json_sidecar.read_text(encoding="utf-8"))

    # LLM judge: Does the structured JSON look like a reasonable tailored resume given the sources and page text length?\n
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
    verdict = _judge_with_llm(judge_prompt, model=ollama_model).strip().upper()
    assert verdict.startswith("PASS"), f"LLM judge did not approve tailored resume. Verdict: {verdict}"
