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

Key dependencies include: langchain-ollama, requests, beautifulsoup4, weasyprint, jinja2, pydantic, python-dotenv. The LangChain integration is provided via the langchain-ollama package.

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
- You can also pass explicit packages instead of using requirements.txt: `python -m scripts.check_library_activity --packages langchain-ollama jinja2`.
- Set a GitHub token via GH_TOKEN or GITHUB_TOKEN env var to raise rate limits.

## Configuration

Set environment variables or a `.env` file in the project root:

- OLLAMA_BASE_URL (default: http://localhost:11434)
- OLLAMA_MODEL (default: gpt-oss)
- LLM_TEMPERATURE (default: 0.2)
- OLLAMA_NUM_CTX (default: 8192) — increases the model context window used for requests to reduce truncation issues with larger prompts.

These defaults are loaded via `resume_builder.config.settings`.

## Running tests

```
pip install -r requirements.txt
pytest -q
```

Live system tests are separated to avoid long, slow runs by default. You can also run a manual live system script with extra debug:

```
python -m scripts.system_live_test --verbose
```

Options:
- --model MODEL           Ollama model to use (default: gemma3:4b-it-q8_0)
- --only {review,activity,resume}  Run just one check
- --work-dir PATH        Directory for outputs (default: ./.live_runs)

Note: the live checks assume an Ollama server is running and the chosen model is available locally. If Ollama is unreachable, the script will print a skip message and exit 0.

Logging: The live test script now logs the exact prompt sent to the LLM right before invocation (truncated to 1000 characters) along with the model name. This is printed to stdout with the prefix [llm]. Be mindful of sensitive information in prompts when sharing logs.

## Maintenance notes

- All `.txt` files in `data/` are ingested automatically (e.g., `experience.txt`, `skills.txt`, `certifications.txt`, `work history.txt`).
- PDF generation uses WeasyPrint (HTML -> PDF). If WeasyPrint is unavailable or you specify a non-PDF extension, the script writes an `.html` file as a fallback.

Suggested cleanup (optional): Review and delete any unused artifacts in your local clone to keep the repo tidy.
- scripts/.live_runs/ contents are ephemeral outputs produced by scripts.system_live_test; you can safely delete files under this directory at any time.
- data/* sample files can be pruned to only those you actually use; the code simply ingests whatever .txt files are present.
- If you have legacy test files relocated into scripts/ (e.g., an older tests/test_system_scripts_live.py), remove the obsolete copy if it still exists outside scripts/.
