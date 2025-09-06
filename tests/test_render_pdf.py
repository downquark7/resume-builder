from pathlib import Path
from resume_builder.render.pdf import render_resume_pdf


def test_render_resume_html_fallback(tmp_path: Path):
    data = {
        "name": "Test User",
        "summary": "Summary text",
        "skills": ["Python"],
        "experience": ["Did X"],
        "projects": ["Proj"],
        "education": ["School"],
        "extras": ["Extra"],
    }
    out_path = tmp_path / "resume.html"
    res = render_resume_pdf(data, out_path)
    assert res.exists()
    text = res.read_text(encoding="utf-8")
    assert "Test User" in text
    assert "Summary" in text
