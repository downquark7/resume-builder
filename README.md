# Resume Builder (LangChain + Ollama)

This project assembles a tailored resume PDF from a job posting URL and a local `data/` directory containing source information (e.g., `projects.txt`, `transcript.txt`). It also provides a script to review each data file and suggest improvements.

Ollama (running in Docker) is used as the LLM backend via LangChain.

## Project structure

- data/
  - projects.txt
  - transcript.txt
- src/
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
      - templates.py
    - chains/
      - __init__.py
      - tailor_resume.py
      - review_file.py
    - render/
      - __init__.py
      - pdf.py
  - scripts/
    - fetch_job_and_build_resume.py
    - review_data_files.py

## Installation

1) Create/activate a virtual environment and install dependencies:

```
pip install -r requirements.txt
```

Dependencies include: langchain, langchain-community, requests, beautifulsoup4, weasyprint (or reportlab), jinja2, pydantic, python-dotenv.

2) Ensure Ollama is running in Docker and exposes its HTTP API to the host (default http://localhost:11434). Install desired models (e.g., `llama3`, `llama3.1`, `mistral`):

```
# inside the Ollama container or via host
ollama pull llama3
```

## Usage

- Build tailored resume PDF from job URL and local data:

```
python -m src.scripts.fetch_job_and_build_resume \
  --url "https://example.com/jobs/123" \
  --data-dir ./data \
  --out ./resume.pdf \
  --model gpt-oss \
  --temperature 0.2
```

- Review each file in `data/` and output suggestions:

```
python -m src.scripts.review_data_files \
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

You can set environment variables or a `.env` file in the project root:

- OLLAMA_BASE_URL (default: http://localhost:11434)
- OLLAMA_MODEL (default: gpt-oss)
- LLM_TEMPERATURE (default: 0.2)

## Running tests

- Install dev dependencies and run pytest:

```
pip install -r requirements.txt
pytest
```

## Notes

- The `transcript.txt` and `projects.txt` in `data/` are simple text sources. You can add more files (e.g., `experience.txt`, `skills.txt`, `certifications.txt`). The system will ingest all `.txt` files.
- PDF generation can be done with WeasyPrint (HTML -> PDF). If WeasyPrint is not available in your environment, the script will fallback to saving an `.html` file for manual conversion.
