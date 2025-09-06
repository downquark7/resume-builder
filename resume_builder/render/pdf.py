from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from jinja2 import Template

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
    """Render a simple resume PDF from structured data.

    Expected data keys: summary (str), skills (list[str]), experience (list[str]),
    projects (list[str]), education (list[str]), extras (list[str]), name (optional str).
    """
    out = Path(out_path)
    html_str = RESUME_HTML_TEMPLATE.render(**data)

    if WEASY_AVAILABLE and out.suffix.lower() == ".pdf":
        HTML(string=html_str).write_pdf(str(out))
    else:
        # Fallback: write HTML instead of PDF
        if out.suffix.lower() != ".html":
            out = out.with_suffix('.html')
        out.write_text(html_str, encoding="utf-8")

    return out
