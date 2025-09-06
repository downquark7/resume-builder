from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    # Default to the gpt-oss model unless overridden via OLLAMA_MODEL
    ollama_model: str = os.getenv("OLLAMA_MODEL", "gpt-oss")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))


settings = Settings()
