from __future__ import annotations
import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from ..llm import ollama_client
from ..prompts.loader import load_prompt


_JSON_KEYS = ["summary", "skills", "experience", "projects", "education", "extras"]


def _extract_json_block(text: str) -> dict | None:
    try:
        return json.loads(text)
    except Exception:
        pass
    import re
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def _empty_resume_state() -> Dict[str, Any]:
    return {"summary": "", "skills": [], "experience": [], "projects": [], "education": [], "extras": []}


def _coerce_resume_state(d: Dict[str, Any]) -> Dict[str, Any]:
    # Ensure proper types and simple normalization
    out = _empty_resume_state()
    if isinstance(d.get("summary"), str):
        out["summary"] = d.get("summary", "")
    # Normalize list-like fields
    for k in ["skills", "experience", "projects", "education", "extras"]:
        v = d.get(k)
        if isinstance(v, list):
            out[k] = [str(x).strip() for x in v if str(x).strip()]
        elif isinstance(v, str) and v.strip():
            out[k] = [v.strip()]
    return out


def tailor_resume_json(job_text: str, sources: Dict[str, str], model: str | None = None, temperature: float | None = None) -> Dict[str, Any]:
    """
    Build a tailored resume JSON by processing one source file at a time in an LLM-decided order,
    progressively updating the resume state after each file.

    Returns a dict with keys: summary, skills, experience, projects, education, extras.
    """
    llm = ollama_client.get_ollama_chat(model=model, temperature=temperature)

    # 1) Decide processing order using the LLM (fallback: given order)
    file_names: List[str] = list(sources.keys())
    order_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You will be given a list of source file names that describe a candidate. "
            "Return ONLY a JSON array of those names ordered by their expected impact on tailoring a resume for the given job."
        ),
        HumanMessagePromptTemplate.from_template(
            "Job description:\n{job}\n\nFiles: {files}\n\nReturn JSON array only (e.g., [\"skills\", \"projects\"])."
        ),
    ])
    try:
        order_messages = order_prompt.format_messages(job=job_text, files=json.dumps(file_names, ensure_ascii=False))
        order_raw = llm.invoke(order_messages)
        order_text = order_raw.content if hasattr(order_raw, "content") else str(order_raw)
        order_list = json.loads(order_text)
        if isinstance(order_list, list) and all(isinstance(x, str) for x in order_list):
            ordered_files = [x for x in order_list if x in sources]
            # Append any missing files to ensure all are processed
            ordered_files += [x for x in file_names if x not in ordered_files]
        else:
            ordered_files = file_names
    except Exception:
        ordered_files = file_names

    # 2) Progressive building: one LLM request per file, updating the state
    state = _empty_resume_state()
    step_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            load_prompt("tailoring_system") +
            "\n\nIMPORTANT: You will be given a single source file and the current partial resume JSON. "
            "Update the JSON by incorporating only relevant, non-duplicated information from the file for the given job. "
            "Return JSON only."
        ),
        HumanMessagePromptTemplate.from_template(
            load_prompt("tailoring_human") +
            "\n\nCURRENT_RESUME_JSON:\n{state}\n\nSOURCE_NAME: {name}\nSOURCE_CONTENT:\n{content}\n\nReturn ONLY the updated JSON."
        ),
    ])

    for fname in ordered_files:
        content = sources.get(fname, "")
        try:
            messages = step_prompt.format_messages(
                job=job_text,
                sources=json.dumps({fname: content}, ensure_ascii=False, indent=2),
                state=json.dumps(state, ensure_ascii=False, indent=2),
                name=fname,
                content=content,
            )
            raw = llm.invoke(messages)
            raw_text = raw.content if hasattr(raw, "content") else str(raw)
            parsed = _extract_json_block(raw_text)
            if parsed:
                state = _coerce_resume_state(parsed)
            # If parsing fails, keep previous state
        except Exception:
            # Keep state unchanged on failure and continue
            continue

    # Final sanity: ensure all required keys exist
    for k in _JSON_KEYS:
        state.setdefault(k, [] if k != "summary" else "")

    return state
