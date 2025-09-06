from __future__ import annotations
import re
import requests
from bs4 import BeautifulSoup


def clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def fetch_job_text(url: str, timeout: int = 20) -> str:
    """Fetches a job description page and returns cleaned main text.
    Very lightweight heuristic: extract <main>, then <article>, then body text.
    """
    resp = requests.get(url, timeout=timeout, headers={
        "User-Agent": "resume-builder/0.1 (+https://github.com/)"
    })
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Prefer main/article/section that looks like job content
    candidates = []
    for sel in ["main", "article", "section", "div[id*=job]", "div[class*=job]"]:
        for el in soup.select(sel):
            txt = el.get_text(" ", strip=True)
            if len(txt) > 300:
                candidates.append(txt)
    if candidates:
        candidates.sort(key=len, reverse=True)
        return clean_text(candidates[0])

    body_text = soup.get_text(" ", strip=True)
    return clean_text(body_text)
