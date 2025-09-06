from __future__ import annotations
import pytest
from resume_builder.config import settings


def pytest_addoption(parser):
    parser.addoption(
        "--ollama-model",
        action="store",
        default=None,
        help="Override the Ollama model used by live system tests (defaults to settings.ollama_model)",
    )


@pytest.fixture(scope="session")
def ollama_model(pytestconfig) -> str:
    """Model to use for live LLM system tests.
    Can be overridden via --ollama-model, otherwise falls back to Settings.ollama_model.
    Example: pytest -k system_scripts_live --ollama-model "gemma3:4b-it-q8_0"
    """
    return pytestconfig.getoption("--ollama-model") or settings.ollama_model
