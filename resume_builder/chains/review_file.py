from __future__ import annotations
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..llm import ollama_client
from ..prompts.loader import load_prompt


def review_source_file(name: str, content: str, model: str | None = None, temperature: float | None = None) -> str:
    llm = ollama_client.get_ollama_chat(model=model, temperature=temperature)
    system_t = SystemMessagePromptTemplate.from_template(load_prompt("review_system"))
    human_t = HumanMessagePromptTemplate.from_template(load_prompt("review_human"))
    prompt = ChatPromptTemplate.from_messages([system_t, human_t])
    messages = prompt.format_messages(name=name, content=content)
    raw = llm.invoke(messages)
    return raw.content if hasattr(raw, "content") else raw
