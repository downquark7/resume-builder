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


def test_render_formats_dict_entries_and_no_raw_dict(tmp_path: Path):
    data = {
        "name": "User",
        "summary": "",
        "skills": [],
        "experience": [
            {"name": "VIN Tracking Database", "description": "Designed and implemented."},
            {"title": "Engineer", "company": "Acme", "description": "Built things"},
        ],
        "projects": [],
        "education": [],
        "extras": [],
    }
    out_path = tmp_path / "resume.html"
    res = render_resume_pdf(data, out_path)
    html = res.read_text(encoding="utf-8")
    assert "{'name':" not in html
    assert "VIN Tracking Database — Designed and implemented." in html
    assert "Engineer, Acme — Built things" in html


def test_render_strips_stray_bullets(tmp_path: Path):
    data = {
        "name": "User",
        "summary": "",
        "skills": ["• Python", "- Java", "* C++", "•"],
        "experience": [],
        "projects": [],
        "education": [],
        "extras": [],
    }
    res = render_resume_pdf(data, tmp_path / "resume.html")
    html = res.read_text(encoding="utf-8")
    # Bullet glyph should be stripped from items and standalone bullets removed
    assert "<li>Python</li>" in html
    assert "<li>Java</li>" in html
    assert "<li>C++</li>" in html
    assert "<li>•</li>" not in html


def test_projects_dedup_against_experience(tmp_path: Path):
    data = {
        "name": "User",
        "summary": "",
        "skills": [],
        "experience": [
            {"name": "MISS", "description": "A CNN system"}
        ],
        "projects": [
            {"name": "MISS", "description": "A CNN system (project)"},
            {"name": "Other", "description": "Different"}
        ],
        "education": [],
        "extras": [],
    }
    res = render_resume_pdf(data, tmp_path / "resume.html")
    html = res.read_text(encoding="utf-8")
    # Project with same title 'MISS' should be removed from Projects
    # Keep 'Other' project
    assert "Other — Different" in html
    # Ensure MISS appears only once (under Experience)
    assert html.count("MISS") == 1
