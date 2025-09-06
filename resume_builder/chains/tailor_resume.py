from __future__ import annotations
import json
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..llm import ollama_client
from ..prompts.loader import load_prompt


def tailor_resume_json(job_text: str, sources: Dict[str, str], model: str | None = None, temperature: float | None = None) -> Dict[str, Any]:
    llm = ollama_client.get_ollama_chat(model=model, temperature=temperature)
    system_t = SystemMessagePromptTemplate.from_template(load_prompt("tailoring_system"))
    human_t = HumanMessagePromptTemplate.from_template(load_prompt("tailoring_human"))
    prompt = ChatPromptTemplate.from_messages([system_t, human_t])

    sources_str = json.dumps(sources, ensure_ascii=False, indent=2)
    messages = prompt.format_messages(job=job_text, sources=sources_str)
    raw = llm.invoke(messages)
    # Extract text from LangChain message objects if necessary
    if hasattr(raw, "content"):
        raw_text = raw.content
    else:
        raw_text = raw

    # Try to parse JSON strictly; fallback: find JSON block
    try:
        return json.loads(raw_text)
    except Exception:
        # naive extraction
        import re
        m = re.search(r"\{[\s\S]*\}", raw_text)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        raise ValueError("LLM did not return valid JSON for tailored resume.")
