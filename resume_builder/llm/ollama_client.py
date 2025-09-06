from __future__ import annotations
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
from ..config import settings


def get_ollama_chat(model: Optional[str] = None, temperature: Optional[float] = None) -> BaseChatModel:
    """
    Returns a LangChain ChatOllama configured for the running Ollama server.
    """
    return ChatOllama(
        base_url=settings.ollama_base_url,
        model=model or settings.ollama_model,
        temperature=settings.llm_temperature if temperature is None else temperature,
        num_ctx=settings.ollama_num_ctx,
    )
