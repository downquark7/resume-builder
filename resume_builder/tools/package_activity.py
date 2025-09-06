from __future__ import annotations
import dataclasses
import datetime as dt
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import requests


REQ_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)")


def parse_requirements(req_path: str | Path) -> List[str]:
    """Parse requirement names from a requirements.txt, ignoring version pins and markers.
    Returns a list of package names as they appear on PyPI.
    """
    names: List[str] = []
    for line in Path(req_path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Remove extras like "; sys_platform != 'win32'"
        line = line.split(";")[0].strip()
        m = REQ_LINE_RE.match(line)
        if not m:
            continue
        name = m.group(1)
        if name:  # skip local paths or links (very naive)
            names.append(name)
    return names


@dataclass
class ProjectURLs:
    homepage: Optional[str] = None
    documentation: Optional[str] = None
    source: Optional[str] = None


@dataclass
class PyPIInfo:
    name: str
    version: Optional[str]
    last_release: Optional[dt.datetime]
    urls: ProjectURLs


@dataclass
class GitHubInfo:
    repo: str  # owner/repo
    html_url: str
    pushed_at: Optional[dt.datetime]
    updated_at: Optional[dt.datetime]


def _parse_iso8601(s: Optional[str]) -> Optional[dt.datetime]:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def fetch_pypi_info(package: str, timeout: int = 15) -> PyPIInfo:
    url = f"https://pypi.org/pypi/{package}/json"
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "resume-builder-activity/0.1"})
    if r.status_code != 200:
        return PyPIInfo(name=package, version=None, last_release=None, urls=ProjectURLs())
    data = r.json()

    info = data.get("info", {})
    releases = data.get("releases", {})

    # Determine latest version and last release upload time
    version = info.get("version")
    last_release: Optional[dt.datetime] = None
    if isinstance(releases, dict):
        # Find latest upload time across all releases
        latest: Optional[dt.datetime] = None
        for _ver, files in releases.items():
            if not isinstance(files, list):
                continue
            for f in files:
                uploaded = _parse_iso8601(f.get("upload_time_iso_8601") or f.get("upload_time"))
                if uploaded and (latest is None or uploaded > latest):
                    latest = uploaded
        last_release = latest

    urls = parse_project_urls(info.get("project_urls") or {})
    return PyPIInfo(name=info.get("name") or package, version=version, last_release=last_release, urls=urls)


def parse_project_urls(project_urls: Dict[str, str]) -> ProjectURLs:
    urls = ProjectURLs()
    for k, v in project_urls.items():
        lk = k.lower()
        if "home" in lk:
            urls.homepage = v
        elif "doc" in lk:
            urls.documentation = v
        elif "source" in lk or "code" in lk:
            urls.source = v
        # capture GitHub if specific keys are used
        if "github" in v.lower():
            urls.source = v
    return urls


GITHUB_REPO_RE = re.compile(r"https?://github\.com/([^/]+/[^/#?]+)")


def find_github_repo(url: Optional[str]) -> Optional[str]:
    if not url:
        return None
    m = GITHUB_REPO_RE.search(url)
    if not m:
        return None
    repo = m.group(1)
    # strip trailing .git
    if repo.endswith('.git'):
        repo = repo[:-4]
    return repo


def fetch_github_repo_info(repo: str, timeout: int = 15, token: Optional[str] = None) -> Optional[GitHubInfo]:
    api_url = f"https://api.github.com/repos/{repo}"
    headers = {"User-Agent": "resume-builder-activity/0.1"}
    if token is None:
        token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(api_url, timeout=timeout, headers=headers)
    if r.status_code != 200:
        return None
    data = r.json()
    return GitHubInfo(
        repo=repo,
        html_url=data.get("html_url", f"https://github.com/{repo}"),
        pushed_at=_parse_iso8601(data.get("pushed_at")),
        updated_at=_parse_iso8601(data.get("updated_at")),
    )


@dataclass
class ActivityAssessment:
    status: str  # Active | Quiet | Potentially Abandoned | Unknown
    reason: str


def classify_activity(
    last_release: Optional[dt.datetime],
    gh_pushed_at: Optional[dt.datetime],
    months_active: int = 12,
    months_quiet: int = 24,
    now: Optional[dt.datetime] = None,
) -> ActivityAssessment:
    if now is None:
        now = dt.datetime.now(dt.timezone.utc)
    def months_since(ts: Optional[dt.datetime]) -> Optional[float]:
        if not ts:
            return None
        # Ensure timezone-aware
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=dt.timezone.utc)
        delta = now - ts
        return delta.days / 30.4375

    m_rel = months_since(last_release)
    m_push = months_since(gh_pushed_at)

    # If GitHub shows recent push, prefer that signal
    if m_push is not None and m_push <= months_active:
        return ActivityAssessment("Active", f"Recent GitHub push {m_push:.1f} months ago")

    # Use PyPI release info
    if m_rel is None and m_push is None:
        return ActivityAssessment("Unknown", "No release or repo activity data available")

    if m_rel is not None and m_rel <= months_active:
        return ActivityAssessment("Active", f"Recent PyPI release {m_rel:.1f} months ago")

    if (m_rel is not None and m_rel <= months_quiet) or (m_push is not None and m_push <= months_quiet):
        return ActivityAssessment("Quiet", "Updated within ~2 years but not in last year")

    return ActivityAssessment("Potentially Abandoned", "No updates in over ~2 years on PyPI/GitHub")


def build_report(packages: Iterable[str], months_active: int = 12, months_quiet: int = 24) -> str:
    lines: List[str] = []
    lines.append("# Dependency Activity Report\n")
    lines.append(f"Checked packages: {', '.join(packages)}\n\n")
    for pkg in packages:
        pypi = fetch_pypi_info(pkg)
        gh_repo = find_github_repo(pypi.urls.source or pypi.urls.homepage or pypi.urls.documentation)
        gh: Optional[GitHubInfo] = fetch_github_repo_info(gh_repo) if gh_repo else None
        assessment = classify_activity(pypi.last_release, gh.pushed_at if gh else None, months_active, months_quiet)

        lines.append(f"## {pypi.name}\n\n")
        lines.append(f"- PyPI: https://pypi.org/project/{pkg}/\n")
        if pypi.version:
            lines.append(f"- Latest version: {pypi.version}\n")
        if pypi.last_release:
            lines.append(f"- Last release: {pypi.last_release.isoformat()}\n")
        if pypi.urls.homepage:
            lines.append(f"- Homepage: {pypi.urls.homepage}\n")
        if pypi.urls.documentation:
            lines.append(f"- Docs: {pypi.urls.documentation}\n")
        if gh:
            lines.append(f"- GitHub: {gh.html_url}\n")
            if gh.pushed_at:
                lines.append(f"- GitHub pushed_at: {gh.pushed_at.isoformat()}\n")
        lines.append(f"- Activity status: {assessment.status} — {assessment.reason}\n\n")
    return "".join(lines)
