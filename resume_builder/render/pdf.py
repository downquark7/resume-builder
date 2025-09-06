from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import os
import json
import re
from jinja2 import Template
try:
    from ..llm import ollama_client  # optional
except Exception:
    ollama_client = None  # type: ignore

try:
    from weasyprint import HTML  # type: ignore
    WEASY_AVAILABLE = True
except Exception:
    WEASY_AVAILABLE = False


RESUME_HTML_TEMPLATE = Template(
    """
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        body { font-family: sans-serif; margin: 32px; }
        h1, h2 { margin-bottom: 6px; }
        .section { margin-top: 16px; }
        ul { margin: 6px 0 0 18px; }
      </style>
    </head>
    <body>
      <h1>{{ name or 'Your Name' }}</h1>
      {% if summary %}
      <div class="section">
        <h2>Summary</h2>
        <p>{{ summary }}</p>
      </div>
      {% endif %}

      {% if skills %}
      <div class="section">
        <h2>Skills</h2>
        <ul>
          {% for s in skills %}<li>{{ s }}</li>{% endfor %}
        </ul>
      </div>
      {% endif %}

      {% if experience %}
      <div class="section">
        <h2>Experience</h2>
        <ul>
          {% for e in experience %}<li>{{ e }}</li>{% endfor %}
        </ul>
      </div>
      {% endif %}

      {% if projects %}
      <div class="section">
        <h2>Projects</h2>
        <ul>
          {% for p in projects %}<li>{{ p }}</li>{% endfor %}
        </ul>
      </div>
      {% endif %}

      {% if education %}
      <div class="section">
        <h2>Education</h2>
        <ul>
          {% for ed in education %}<li>{{ ed }}</li>{% endfor %}
        </ul>
      </div>
      {% endif %}

      {% if extras %}
      <div class="section">
        <h2>Additional</h2>
        <ul>
          {% for x in extras %}<li>{{ x }}</li>{% endfor %}
        </ul>
      </div>
      {% endif %}
    </body>
    </html>
    """
)


def render_resume_pdf(data: Dict[str, Any], out_path: str | Path) -> Path:
    """Render a resume PDF/HTML from structured data.

    Expected data keys: summary (str), skills (list[str]|str), experience (list[str]|str),
    projects (list[str]|str), education (list[str]|str), extras (list[str]|str), name (optional str).

    Behavior:
    - By default uses a simple Jinja2 template (stable, deterministic) after normalizing inputs.
    - If environment variable RENDER_WITH_LLM=true or data["llm_render"] is truthy AND an LLM client is available,
      delegates the final HTML composition to the LLM so it can decide ordering and how many items to include
      (especially slimming projects). If the LLM call fails, falls back to the template.
    - Regardless of the path, list fields are normalized and projects are deduped against experience by title.
    """
    bullet_re = re.compile(r"^\s*[\u2022•\-*]+\s*")

    def _format_dict(d: dict) -> str:
        # Try to compose a readable line from common fields
        title_keys = ("title", "role", "position", "name")
        org_keys = ("company", "organization", "employer")
        desc_keys = ("description", "desc", "details", "text")
        edu_keys = ("degree", "major", "university", "college")

        title = next((str(d[k]).strip() for k in title_keys if k in d and str(d[k]).strip()), "")
        org = next((str(d[k]).strip() for k in org_keys if k in d and str(d[k]).strip()), "")
        desc = next((str(d[k]).strip() for k in desc_keys if k in d and str(d[k]).strip()), "")

        if title or org or desc:
            parts = []
            head = title or org
            if title and org:
                head = f"{title}, {org}"
            if head:
                parts.append(head)
            if desc:
                parts.append(desc)
            return " — ".join(parts)

        # Education-specific
        edu_vals = [str(d[k]).strip() for k in edu_keys if k in d and str(d[k]).strip()]
        if edu_vals:
            return " — ".join(edu_vals)

        # Fallback: key: value; ... but avoid braces
        kv_parts = []
        for k, v in d.items():
            s = str(v).strip()
            if s:
                kv_parts.append(f"{k}: {s}")
        return "; ".join(kv_parts) if kv_parts else ""

    def _format_item(x: Any) -> list[str]:
        # Return a list of formatted strings (may flatten nested lists)
        if x is None:
            return []
        if isinstance(x, str):
            s = x.strip()
            if not s:
                return []
            s = bullet_re.sub("", s)  # strip leading bullet glyphs
            return [s] if s else []
        if isinstance(x, dict):
            s = bullet_re.sub("", _format_dict(x))
            return [s] if s else []
        if isinstance(x, list):
            out: list[str] = []
            for item in x:
                out.extend(_format_item(item))
            return out
        # other types
        s = bullet_re.sub("", str(x).strip())
        return [s] if s else []

    def _to_list(v: Any) -> list[str]:
        items = _format_item(v)
        # filter standalone bullets or empties
        items = [i for i in items if i and i not in {"•", "-", "*"}]
        return items

    def _dedupe_preserve_order(items: list[str]) -> list[str]:
        seen = set()
        result: list[str] = []
        for x in items:
            if x not in seen:
                seen.add(x)
                result.append(x)
        return result

    def _base_title(s: str) -> str:
        # Use part before an em dash or colon as title, lowercased
        s0 = s.split(" — ", 1)[0]
        s0 = s0.split(": ", 1)[0]
        return s0.strip().lower()

    normalized = dict(data)
    for key in ("skills", "experience", "projects", "education", "extras"):
        normalized[key] = _dedupe_preserve_order(_to_list(data.get(key)))

    # Cross-dedupe: remove projects that duplicate experience by title
    exp_titles = {_base_title(x) for x in normalized.get("experience", []) if x}
    normalized["projects"] = [p for p in normalized.get("projects", []) if _base_title(p) not in exp_titles]

    # Ensure summary is a string
    summary = normalized.get("summary", "")
    if not isinstance(summary, str):
        normalized["summary"] = str(summary)

    out = Path(out_path)

    # Decide whether to ask an LLM to compose the final HTML
    use_llm = False
    try:
        use_llm = bool(str(os.getenv("RENDER_WITH_LLM", "")).lower() in {"1", "true", "yes"} or data.get("llm_render")) and ollama_client is not None
    except Exception:
        use_llm = False

    html_str: str | None = None

    if use_llm:
        try:
            # Compose minimal, strict instruction to produce concise, well-ordered HTML.
            # Provide normalized data so the model can choose what to include and how many items.
            payload = {
                "name": normalized.get("name", ""),
                "summary": normalized.get("summary", ""),
                "skills": normalized.get("skills", []),
                "experience": normalized.get("experience", []),
                "projects": normalized.get("projects", []),
                "education": normalized.get("education", []),
                "extras": normalized.get("extras", []),
            }
            instruction = (
                "You are an expert resume editor. Create the final HTML for a 1-page resume using the provided structured data.\n"
                "Decide: which sections to include, how many items from each (keep it concise), the order of sections, and phrasing.\n"
                "Specifically slim down projects to only the most impactful items. Remove duplicates.\n"
                "Output ONLY valid, self-contained HTML (no Markdown, no code fences). Include minimal inline CSS for readability.\n"
                "Use <h1> for the candidate name, <h2> for section headers, and <ul><li> for lists."
            )
            data_json = json.dumps(payload, ensure_ascii=False, indent=2)
            prompt_text = (
                f"SYSTEM:\n{instruction}\n\n"
                f"DATA (JSON):\n{data_json}\n\n"
                "Constraints:\n"
                "- Decide the ordering of the entire output.\n"
                "- Decide how many items per section to prevent excessive length.\n"
                "- Prefer merging redundant items and removing near-duplicates.\n"
                "- If a section is empty after pruning, omit it.\n"
                "- Keep language tight and impact-focused.\n"
                "Return only HTML."
            )

            llm = ollama_client.get_ollama_chat()
            raw = llm.invoke(prompt_text)
            text = raw.content if hasattr(raw, "content") else str(raw)
            text = text.strip()
            # Strip common code fences if present
            if text.startswith("```"):
                text = re.sub(r"^```[a-zA-Z]*\n?|\n?```$", "", text, flags=re.MULTILINE).strip()
            # Ensure we have an <html> root
            if "<html" not in text.lower():
                # Wrap as minimal HTML
                body = text
                text = (
                    "<html><head><meta charset=\"utf-8\" />"
                    "<style>body{font-family:sans-serif;margin:32px;} h1,h2{margin-bottom:6px;} .section{margin-top:16px;} ul{margin:6px 0 0 18px;}</style>"
                    "</head><body>" + body + "</body></html>"
                )
            html_str = text
        except Exception:
            html_str = None

    if not html_str:
        html_str = RESUME_HTML_TEMPLATE.render(**normalized)

    if WEASY_AVAILABLE and out.suffix.lower() == ".pdf":
        HTML(string=html_str).write_pdf(str(out))
    else:
        # Fallback: write HTML instead of PDF
        if out.suffix.lower() != ".html":
            out = out.with_suffix('.html')
        out.write_text(html_str, encoding="utf-8")

    return out
