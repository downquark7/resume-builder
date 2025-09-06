from __future__ import annotations
import datetime as dt
from types import SimpleNamespace

import json
import re

from resume_builder.tools.package_activity import (
    parse_requirements,
    parse_project_urls,
    find_github_repo,
    classify_activity,
    fetch_pypi_info,
    fetch_github_repo_info,
)


class DummyResp:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json


def test_parse_requirements(tmp_path):
    p = tmp_path / "requirements.txt"
    p.write_text("""
    langchain>=0.2.0
    beautifulsoup4>=4.12.2 ; sys_platform != 'win32'
    # comment
    python-dotenv
    """.strip(), encoding="utf-8")
    names = parse_requirements(p)
    assert names == ["langchain", "beautifulsoup4", "python-dotenv"]


def test_parse_project_urls_and_github_repo():
    urls = parse_project_urls({
        "Homepage": "https://example.com",
        "Documentation": "https://docs.example.com",
        "Source": "https://github.com/org/repo",
    })
    assert urls.homepage and urls.documentation and urls.source
    repo = find_github_repo(urls.source)
    assert repo == "org/repo"


def test_classify_activity_heuristics():
    now = dt.datetime(2025, 9, 5, tzinfo=dt.timezone.utc)
    recent = now - dt.timedelta(days=100)
    old = now - dt.timedelta(days=900)  # ~29.6 months

    # Recent GitHub push => Active
    a = classify_activity(last_release=None, gh_pushed_at=recent, now=now)
    assert a.status == "Active"

    # Recent PyPI release => Active
    a = classify_activity(last_release=recent, gh_pushed_at=None, now=now)
    assert a.status == "Active"

    # Quiet if within 24 months but not within 12
    quiet = now - dt.timedelta(days=int(18 * 30.4375))
    a = classify_activity(last_release=quiet, gh_pushed_at=None, now=now)
    assert a.status == "Quiet"

    # Potentially Abandoned if older than ~24 months
    a = classify_activity(last_release=old, gh_pushed_at=None, now=now)
    assert a.status == "Potentially Abandoned"


def test_fetch_pypi_and_github_info_monkeypatched(monkeypatch):
    # Monkeypatch requests.get for both PyPI and GitHub endpoints
    def fake_get(url, timeout=15, headers=None):
        if "pypi.org/pypi/langchain/json" in url:
            data = {
                "info": {
                    "name": "langchain",
                    "version": "0.2.16",
                    "project_urls": {
                        "Homepage": "https://python.langchain.com",
                        "Source": "https://github.com/langchain-ai/langchain",
                        "Documentation": "https://python.langchain.com/docs/",
                    },
                },
                "releases": {
                    "0.2.16": [
                        {"upload_time_iso_8601": "2025-08-20T12:00:00Z"}
                    ]
                },
            }
            return DummyResp(200, data)
        if "api.github.com/repos/langchain-ai/langchain" in url:
            data = {
                "html_url": "https://github.com/langchain-ai/langchain",
                "pushed_at": "2025-09-01T10:00:00Z",
                "updated_at": "2025-09-01T10:00:00Z",
            }
            return DummyResp(200, data)
        return DummyResp(404, {})

    monkeypatch.setattr("requests.get", fake_get)

    pypi = fetch_pypi_info("langchain")
    assert pypi.version == "0.2.16"
    assert pypi.last_release is not None

    gh = fetch_github_repo_info("langchain-ai/langchain")
    assert gh is not None and gh.pushed_at is not None
