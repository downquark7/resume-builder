from __future__ import annotations
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from ..llm import ollama_client
from ..prompts.loader import load_prompt


def review_source_file(name: str, content: str, model: str | None = None, temperature: float | None = None) -> str:
    """Return a plain-text suggestion for a single source file.

    Uses a simple LCEL chain (prompt | llm | StrOutputParser) to normalize
    various model return shapes into a string, reducing chances of blank output.
    """
    llm = ollama_client.get_ollama_chat(model=model, temperature=temperature)
    system_t = SystemMessagePromptTemplate.from_template(load_prompt("review_system"))
    human_t = HumanMessagePromptTemplate.from_template(load_prompt("review_human"))
    prompt = ChatPromptTemplate.from_messages([system_t, human_t])

    # Build chain that always outputs a string
    chain = prompt | llm | StrOutputParser()
    try:
        return chain.invoke({"name": name, "content": content})
    except Exception:
        # Fallback to direct invocation if needed
        messages = prompt.format_messages(name=name, content=content)
        raw = llm.invoke(messages)
        return raw.content if hasattr(raw, "content") else str(raw)
