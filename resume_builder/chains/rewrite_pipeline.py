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
    print("[LLM] Waiting for model response...")
    llm = ollama_client.get_ollama_chat(model=model, temperature=temperature)
    # Simple single-turn prompt
    resp = llm.invoke(prompt)  # type: ignore[attr-defined]
    # LangChain ChatOllama returns a AIMessage
    content = getattr(resp, "content", None)
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
        prompt = _render(prompt_t, cleaned_job=cleaned_job, category=category, source_text=text)
        result = _call_llm(prompt, cfg.model, cfg.temperature)
        _append_log(cfg.log_file, "shorten_file", result, extra=f"category={category}")
        shortened[category] = result.strip()
    return shortened


def build_yaml_resume(cleaned_job: str, shortened_map: Dict[str, str], cfg: RewriteConfig) -> str:
    prompt_t = load_prompt("build_yaml_resume")
    # Compose a readable shortened_map text block
    parts = []
    for k, v in shortened_map.items():
        parts.append(f"[{k}]\n{v}\n")
    combined = "\n".join(parts)
    prompt = _render(prompt_t, cleaned_job=cleaned_job, shortened_map=combined)
    out = _call_llm(prompt, cfg.model, cfg.temperature)
    _append_log(cfg.log_file, "build_yaml_resume", out)
    return out


def run_rewrite(job_text_or_url: str, data_dir: str | None, cfg: RewriteConfig) -> str:
    # If looks like URL, fetch; otherwise treat as raw text
    raw_job = job_text_or_url
    if job_text_or_url.lower().startswith("http://") or job_text_or_url.lower().startswith("https://"):
        print("Fetching job posting from URL...")
        raw_job = fetch_job_text(job_text_or_url)

    print("Cleaning job description...")
    cleaned = clean_job_description(raw_job, cfg)

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
