from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime

from ..llm import ollama_client
from ..prompts.loader import load_prompt
from ..io.data_loader import load_data_dir
from ..io.job_fetcher import fetch_job_text


@dataclass
class RewriteConfig:
    model: Optional[str] = None
    temperature: Optional[float] = None
    log_file: Optional[str] = None


def _render(template: str, **kwargs) -> str:
    out = template
    for k, v in kwargs.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


def _call_llm(prompt: str, model: Optional[str], temperature: Optional[float]) -> str:
    start = datetime.now()
    model_label = model or "default"
    # Heuristic token count (since no tokenizer dependency is available): whitespace-delimited tokens
    try:
        input_tokens = len(prompt.split())
    except Exception:
        input_tokens = 0
    print(f"[LLM] Sending prompt to model '{model_label}' (temperature={temperature if temperature is not None else 'default'}, input_tokens~{input_tokens})...")
    llm = ollama_client.get_ollama_chat(model=model, temperature=temperature)
    resp = llm.invoke(prompt)  # type: ignore[attr-defined]
    elapsed = (datetime.now() - start).total_seconds()
    # LangChain ChatOllama returns an AIMessage
    content = getattr(resp, "content", None)
    print(f"[LLM] Received response from '{model_label}' in {elapsed:.1f}s, length={len(content) if isinstance(content, str) else 'n/a'} chars.")
    return content if isinstance(content, str) else str(resp)


def _append_log(path: Optional[str], stage: str, content: str, extra: Optional[str] = None) -> None:
    if not path:
        return
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"--- [{ts}] stage={stage}{' ' + extra if extra else ''}\n")
            f.write(content.rstrip() + "\n\n")
    except Exception:
        # Logging must not break pipeline
        pass


def clean_job_description(raw_job_text: str, cfg: RewriteConfig) -> str:
    prompt_t = load_prompt("clean_job_description")
    prompt = _render(prompt_t, raw_job_text=raw_job_text)
    out = _call_llm(prompt, cfg.model, cfg.temperature)
    _append_log(cfg.log_file, "clean_job_description", out)
    return out


def shorten_sources(cleaned_job: str, sources: Dict[str, str], cfg: RewriteConfig) -> Dict[str, str]:
    prompt_t = load_prompt("shorten_file")
    shortened: Dict[str, str] = {}
    for category, text in sources.items():
        if not text.strip():
            continue
        cat_lower = category.lower().strip()
        # Pass-through for contact info and any category whose filename contains 'information'
        # Rationale: any file with 'information' in its name will be short enough that shortening it twice could result in loss of information.
        if "information" in cat_lower:
            raw = text.strip()
            _append_log(cfg.log_file, "shorten_file", raw, extra=f"category={category} (passthrough)")
            shortened[category] = raw
            continue
        prompt = _render(prompt_t, cleaned_job=cleaned_job, category=category, source_text=text)
        result = _call_llm(prompt, cfg.model, cfg.temperature)
        _append_log(cfg.log_file, "shorten_file", result, extra=f"category={category}")
        shortened[category] = result.strip()
    return shortened


def _normalize_skill(s: str) -> str:
    return s.strip().lower()


def _filter_skills_in_yaml(yaml_text: str, allowed_skills: set[str]) -> str:
    """
    Very lightweight post-processor: if a 'skills:' YAML list is present at top level (either at root or under 'content:'),
    drop any items that are not in allowed_skills (normalized). This is a best-effort
    safeguard against LLM adding skills from the job that the user doesn't have.
    Keeps original casing for items that match case-insensitively.
    """
    try:
        import re
        lines = yaml_text.splitlines()
        out_lines = []
        in_skills = False
        current_indent = None
        for i, line in enumerate(lines):
            # Detect start of top-level skills list either at root or under content
            if not in_skills and (re.match(r"^skills:\s*$", line) or re.match(r"^\s{2}skills:\s*$", line) or re.match(r"^\s+skills:\s*$", line)):
                in_skills = True
                current_indent = None
                out_lines.append(line)
                continue
            if in_skills:
                # Determine if line looks like a list item under skills
                if current_indent is None:
                    # The first list item should start with '- ' and define indent
                    m = re.match(r"^(\s*)-\s+(.*)$", line)
                    if m:
                        indent, item = m.group(1), m.group(2)
                        current_indent = indent
                        norm = _normalize_skill(re.sub(r"[,:]$", "", item))
                        # Find original-casing match from allowed_skills
                        keep = any(_normalize_skill(a) == norm for a in allowed_skills)
                        if keep:
                            out_lines.append(line)
                        # else: drop
                        continue
                    else:
                        # skills section ended if indentation changes or key starts
                        in_skills = False
                        current_indent = None
                        out_lines.append(line)
                        continue
                else:
                    # Subsequent items must have same indent
                    m = re.match(r"^(\s*)-\s+(.*)$", line)
                    if m and m.group(1) == current_indent:
                        item = m.group(2)
                        norm = _normalize_skill(re.sub(r"[,:]$", "", item))
                        keep = any(_normalize_skill(a) == norm for a in allowed_skills)
                        if keep:
                            out_lines.append(line)
                        # else: drop
                        continue
                    else:
                        # skills list likely ended
                        in_skills = False
                        current_indent = None
                        out_lines.append(line)
                        continue
            else:
                out_lines.append(line)
        return "\n".join(out_lines)
    except Exception:
        # Fail-open: return original YAML
        return yaml_text


def _sanitize_yaml_output(text: str) -> str:
    """Best-effort fixes to make LLM output pass yamlresume validation without inventing data.
    - Strip markdown code fences if present.
    - Normalize any endDate: Present -> endDate: ''
    - If content.skills is a mapping with 'keywords', convert to a flat list under 'skills'.
    This function operates with simple heuristics on the raw YAML text to avoid adding a YAML parser dependency.
    Fail-open if anything goes wrong.
    """
    try:
        import re
        s = text.strip()
        # Remove fenced code blocks ```...```
        if s.startswith("```"):
            # drop the first fence line and the last matching fence
            s = re.sub(r"^```[\w-]*\n", "", s)
            s = re.sub(r"\n```\s*$", "", s)
        # Normalize Present -> empty endDate
        s = re.sub(r"(?im)^(\s*endDate\s*:\s*)Present\s*$", r"\1", s)
        # Transform skills: keywords mapping into flat list
        # Look for a block like:\n# skills:\n#   keywords:\n#     - A\n#     - B
        skills_block_pattern = re.compile(
            r"(?ms)^(\s*)skills:\s*\n\1\s+keywords:\s*\n((?:\1\s+-\s+.+\n?)+)"
        )
        def repl(m: re.Match) -> str:
            indent = m.group(1)
            items_block = m.group(2)
            # Convert each bullet to a flat list item under skills
            lines = []
            for line in items_block.splitlines():
                t = line.strip()
                if not t:
                    continue
                # line like '- Python'
                val = re.sub(r"^-[\s\t]+", "", t)
                lines.append(f"{indent}  - {val}")
            return f"{indent}skills:\n" + "\n".join(lines) + "\n"
        s = skills_block_pattern.sub(repl, s)
        # Remove any stray grouped skills entries like '- category: ...' that may follow a flattened skills block
        # This crudely drops lines starting with '- category:' and their immediate 'keywords:' sub-block, within the skills indentation context.
        s = re.sub(r"(?ms)^(\s*)-\s*category:.*?(?=\n\1\S|\n\n|\Z)", "", s)
        # s = re.sub(r"C\+\+", r"C\\+\\+", s)
        return s
    except Exception:
        return text


def build_yaml_resume(cleaned_job: str, shortened_map: Dict[str, str], cfg: RewriteConfig) -> str:
    prompt_t = load_prompt("build_yaml_resume")
    # Compose a readable shortened_map text block
    parts = []
    for k, v in shortened_map.items():
        parts.append(f"[{k}]\n{v}\n")
    combined = "\n".join(parts)
    prompt = _render(prompt_t, cleaned_job=cleaned_job, shortened_map=combined)
    out = _call_llm(prompt, cfg.model, cfg.temperature)

    # Post-process to improve YAML compliance before skills filtering
    out = _sanitize_yaml_output(out)

    # Build allowed skills set from shortened_map's 'skills' category (each line is a bullet)
    skills_source = None
    for key in shortened_map.keys():
        if key.strip().lower() in {"skills", "skill", "technical skills"}:
            skills_source = shortened_map[key]
            break
    allowed: set[str] = set()
    if skills_source:
        for line in skills_source.splitlines():
            s = line.strip().lstrip("-•*").strip()
            if s:
                allowed.add(s)
    if allowed:
        filtered = _filter_skills_in_yaml(out, allowed)
        if cfg.log_file:
            _append_log(cfg.log_file, "skills_filter_info", "\n".join(sorted(allowed)), extra="allowed_skills")
    else:
        filtered = out

    _append_log(cfg.log_file, "build_yaml_resume", filtered)
    return filtered


def run_rewrite(job_text_or_url: str | None, data_dir: str | None, cfg: RewriteConfig) -> str:
    # If looks like URL, fetch; otherwise treat as raw text. If not provided, use an empty job description.
    raw_job = job_text_or_url or ""
    if job_text_or_url and (job_text_or_url.lower().startswith("http://") or job_text_or_url.lower().startswith("https://")):
        print("Fetching job posting from URL...")
        raw_job = fetch_job_text(job_text_or_url)

    if raw_job.strip():
        print("Cleaning job description...")
        cleaned = clean_job_description(raw_job, cfg)
    else:
        print("No job description provided; proceeding using data only.")
        cleaned = ""

    sources: Dict[str, str] = {}
    if data_dir:
        print(f"Loading data directory: {data_dir}")
        sources = load_data_dir(data_dir)

    print("Creating shortened selections for each data file...")
    shortened = shorten_sources(cleaned, sources, cfg)

    print("Building YAML resume...")
    yaml_doc = build_yaml_resume(cleaned, shortened, cfg)

    # Also log the final YAML to the same log file for convenience
    _append_log(cfg.log_file, "final_yaml", yaml_doc)
    return yaml_doc
