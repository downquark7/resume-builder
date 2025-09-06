from __future__ import annotations
import sys
from pathlib import Path
import types

import builtins


def test_fetch_job_and_build_resume_cli(monkeypatch, tmp_path):
    # Import module under test
    import scripts.fetch_job_and_build_resume as mod

    # Stub dependencies to avoid network/LLM/PDF
    monkeypatch.setattr(mod, "fetch_job_text", lambda url: "JOB TEXT" )
    monkeypatch.setattr(mod, "load_data_dir", lambda d: {"name": "Jane Dev", "projects": "x", "skills": "y"})

    # Tailored JSON the LLM would have returned
    tailored = {
        "summary": "A summary",
        "skills": ["Python"],
        "experience": ["Did X"],
        "projects": ["Proj"],
        "education": ["School"],
        "extras": ["Extra"],
    }
    monkeypatch.setattr(mod, "tailor_resume_json", lambda job, sources, model=None, temperature=None: tailored)

    out_pdf = tmp_path / "resume.pdf"

    # render_resume_pdf should create a file and return its path
    def fake_render(data, out_path):
        p = Path(out_path)
        # Ensure suffix handling is respected by implementation
        if p.suffix.lower() != ".html" and p.suffix.lower() != ".pdf":
            p = p.with_suffix(".html")
        p.write_text("HTML CONTENT", encoding="utf-8")
        return p

    monkeypatch.setattr(mod, "render_resume_pdf", fake_render)

    # Run CLI main with args
    argv = [
        "prog",
        "--url", "https://example.com/job",
        "--data-dir", str(tmp_path),
        "--out", str(out_pdf),
        "--model", "gpt-oss",
        "--temperature", "0.2",
    ]
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")
    monkeypatch.setattr(sys, "argv", argv)

    mod.main()

    # JSON sidecar should be next to provided --out (.json)
    json_path = out_pdf.with_suffix(".json")
    assert json_path.exists(), "Expected sidecar JSON to be written"
    text = json_path.read_text(encoding="utf-8")
    assert "summary" in text and "skills" in text

    # Rendered file should exist (pdf or html depending on fake renderer)
    # Our fake renderer always writes to requested suffix or .html fallback
    # Check either the specified path or .html if differing
    html_candidate = out_pdf if out_pdf.exists() else out_pdf.with_suffix(".html")
    assert html_candidate.exists(), "Expected rendered output file"


def test_review_data_files_cli(monkeypatch, tmp_path):
    import scripts.review_data_files as mod

    # Mock data loader to simulate multiple files
    monkeypatch.setattr(mod, "load_data_dir", lambda d: {"projects": "P text", "skills": "S text"})
    # Mock review chain to return deterministic suggestion
    monkeypatch.setattr(mod, "review_source_file", lambda name, content, model=None, temperature=None: f"Suggestion for {name}")

    out_md = tmp_path / "suggestions.md"
    argv = [
        "prog",
        "--data-dir", str(tmp_path),
        "--out", str(out_md),
        "--model", "gpt-oss",
        "--temperature", "0.3",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    mod.main()

    assert out_md.exists()
    content = out_md.read_text(encoding="utf-8")
    # Should include headings per file and the suggestion text
    assert "## projects" in content
    assert "## skills" in content
    assert "Suggestion for projects" in content
    assert "Suggestion for skills" in content


def test_check_library_activity_cli(monkeypatch, tmp_path):
    import scripts.check_library_activity as mod

    # We prefer passing --packages to bypass reading requirements
    # but we also validate that build_report is called and file written.
    def fake_build_report(packages, months_active=12, months_quiet=24):
        return f"Report for: {', '.join(packages)}\nActive thresholds: {months_active}/{months_quiet}"

    monkeypatch.setattr(mod, "build_report", fake_build_report)

    out_md = tmp_path / "dep.md"
    argv = [
        "prog",
        "--packages", "langchain", "jinja2",
        "--out", str(out_md),
        "--months-active", "10",
        "--months-quiet", "20",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    mod.main()

    assert out_md.exists()
    content = out_md.read_text(encoding="utf-8")
    assert "langchain" in content and "jinja2" in content
    assert "10/20" in content
