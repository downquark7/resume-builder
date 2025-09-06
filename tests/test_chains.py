from resume_builder.chains.tailor_resume import tailor_resume_json
from resume_builder.chains.review_file import review_source_file


def test_tailor_resume_json_returns_required_keys_with_real_llm():
    # Uses the real Ollama model configured via environment (default gpt-oss)
    sources = {
        "projects": "Built a Python web scraper that extracted data and stored it in SQLite.",
        "skills": "Python, Web scraping, SQL",
        "education": "B.Sc. in Computer Science",
    }
    out = tailor_resume_json("Junior Python developer role focusing on data processing and web scraping.", sources)
    assert isinstance(out, dict)
    # Check required keys exist (content may vary)
    for key in ["summary", "skills", "experience", "projects", "education", "extras"]:
        assert key in out


def test_tailor_resume_json_parses_embedded_json(monkeypatch):
    # Monkeypatch the LLM to return non-JSON text with an embedded JSON block
    from resume_builder.chains import tailor_resume as mod

    class FakeLLM:
        def invoke(self, messages):
            # Return text surrounding a JSON payload
            return (
                "Here is your result:\n"
                '{"summary": "S", "skills": ["A"], "experience": [], '
                '"projects": [], "education": [], "extras": []}'
                "\nThanks!"
            )

    monkeypatch.setattr(mod.ollama_client, "get_ollama_chat", lambda model=None, temperature=None: FakeLLM())
    out = mod.tailor_resume_json("job", {"skills": "A"})
    assert out.get("summary") == "S"
    assert out.get("skills") == ["A"]


def test_review_source_file_returns_text_with_real_llm():
    txt = review_source_file(
        "projects",
        "Implemented a data pipeline that ingests JSON logs and aggregates metrics using Python.",
    )
    assert isinstance(txt, str)
    assert len(txt.strip()) > 0
