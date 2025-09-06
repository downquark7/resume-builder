# Resume Builder (LangChain + Ollama)

This project assembles a tailored resume PDF from a job posting URL and a local `data/` directory containing source information (e.g., `projects.txt`, `transcript.txt`, `skills.txt`). It also provides a script to review each data file and suggest improvements, plus a small utility to check the activity status of your Python dependencies.

Ollama (local LLM server) is used as the LLM backend via LangChain.

## Project structure

- data/
  - projects.txt
  - transcript.txt
  - skills.txt
  - extracurriculars.txt
  - work history.txt
- resume_builder/
  - __init__.py
  - config.py
  - llm/
    - __init__.py
    - ollama_client.py
  - io/
    - __init__.py
    - job_fetcher.py
    - data_loader.py
  - prompts/
    - __init__.py
    - loader.py
    - templates.py
    - text/
      - review_system.txt
      - review_human.txt
      - tailoring_system.txt
      - tailoring_human.txt
  - chains/
    - __init__.py
    - tailor_resume.py
    - review_file.py
  - render/
    - __init__.py
    - pdf.py
  - tools/
    - package_activity.py
- scripts/
  - fetch_job_and_build_resume.py
  - review_data_files.py
  - check_library_activity.py
- tests/
  - ...

## Installation

1) Create/activate a virtual environment and install dependencies:

```
pip install -r requirements.txt
```

Key dependencies include: langchain, langchain-community, requests, beautifulsoup4, weasyprint, jinja2, python-dotenv.

2) Ensure Ollama is running and exposes its HTTP API to the host (default http://localhost:11434). Install desired models (e.g., `llama3`, `llama3.1`, `mistral`):

```
ollama pull llama3
```

## Usage

- Build a tailored resume PDF (or HTML fallback) from a job URL and local data:

```
python -m scripts.fetch_job_and_build_resume \
  --url "https://example.com/jobs/123" \
  --data-dir ./data \
  --out ./resume.pdf \
  --model gpt-oss \
  --temperature 0.2
```

- Review each file in `data/` and output suggestions:

```
python -m scripts.review_data_files \
  --data-dir ./data \
  --out suggestions.md \
  --model gpt-oss \
  --temperature 0.3
```

- Generate a dependency activity report (PyPI + GitHub):

```
python -m scripts.check_library_activity \
  --requirements requirements.txt \
  --out dependency_activity.md \
  --months-active 12 \
  --months-quiet 24
```

Notes:
- You can also pass explicit packages instead of using requirements.txt: `python -m scripts.check_library_activity --packages langchain langchain-community langchain-ollama`.
- Set a GitHub token via GH_TOKEN or GITHUB_TOKEN env var to raise rate limits.

## Configuration

Set environment variables or a `.env` file in the project root:

- OLLAMA_BASE_URL (default: http://localhost:11434)
- OLLAMA_MODEL (default: gpt-oss)
- LLM_TEMPERATURE (default: 0.2)

These defaults are loaded via `resume_builder.config.settings`.

## Running tests

```
pip install -r requirements.txt
pytest -q
```

## Notes

- All `.txt` files in `data/` are ingested automatically (e.g., `experience.txt`, `skills.txt`, `certifications.txt`, `work history.txt`).
- PDF generation uses WeasyPrint (HTML -> PDF). If WeasyPrint is unavailable or you specify a non-PDF extension, the script writes an `.html` file as a fallback.
