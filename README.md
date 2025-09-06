# Resume Builder (LangChain + Ollama)

This project assembles a tailored resume PDF (or HTML fallback) from a job posting URL and a local `data/` directory containing your source information (e.g., `projects.txt`, `skills.txt`, `work history.txt`, `contact information.txt`). It also includes:
- A script to review each data file and suggest improvements.
- A utility to check the recent activity of your Python dependencies.

Ollama (local LLM server) is used as the LLM backend via LangChain.

## Project structure

- data/ (your inputs, any `.txt` files are ingested)
  - projects.txt
  - skills.txt
  - extracurriculars.txt
  - work history.txt (alias of experience)
  - contact information.txt (alias of contact)
  - classes taken.txt (optional)
  - degree information.txt (optional)
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
  - system_live_test.py (manual live check)
- tests/
  - ...

## Installation

1) Create/activate a virtual environment and install dependencies:

```
pip install -r requirements.txt
```

Key dependencies include: langchain-ollama, requests, beautifulsoup4, weasyprint, jinja2, pydantic, python-dotenv. The LangChain integration is provided via the `langchain-ollama` package.

2) Ensure Ollama is running and exposes its HTTP API (default http://localhost:11434). Install desired models (e.g., `llama3`, `mistral`, or your preferred compatible model):

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

What happens:
- The job posting is fetched and cleaned.
- All `.txt` files in `--data-dir` are loaded. Some filenames are normalized (aliases):
  - "work history" / "work_history" -> "experience"
  - "contact information" / "contact_information" -> "contact"
- The LLM tailors a structured JSON resume.
- The renderer normalizes lists, deduplicates overlapping projects vs experience, and writes a PDF (or HTML if PDF not available).
- A sidecar `resume.json` (same basename as `--out`) is saved with the raw structured output.

Tip: Put your name into a `name.txt` file to have it appear as the H1 title.

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
- RENDER_WITH_LLM (default: false) — when true, and if the Ollama client is available, the final HTML composition is delegated to the LLM which may re-order sections and trim lists. Otherwise a deterministic Jinja2 template is used.

These defaults are loaded via `resume_builder.config.settings` (except `RENDER_WITH_LLM`, which is read within the renderer).

## Data files

Any `.txt` file under `data/` becomes a key in the prompt using its basename. Common examples:
- name.txt — candidate display name
- skills.txt — bullets or lines
- projects.txt — bullets or lines; can include brief descriptions
- work history.txt — same as experience; alias handled automatically
- contact information.txt — alias to contact
- classes taken.txt, degree information.txt — optional educational details

The system deduplicates exact duplicates and strips leading bullet glyphs (•, -, *). JSON-like strings in LLM output are parsed into lists when rendering.

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
- --model MODEL           Ollama model to use (default: from env OLLAMA_MODEL)
- --only {review,activity,resume}  Run just one check
- --work-dir PATH        Directory for outputs (default: ./.live_runs)

Note: the live checks assume an Ollama server is running and the chosen model is available locally. If Ollama is unreachable, the script will print a skip message and exit 0.

Logging: The live test script logs the prompt (truncated to 1000 chars) with model name to stdout with the prefix [llm]. Be mindful of sensitive information in prompts when sharing logs.

## Maintenance notes

- All `.txt` files in `data/` are ingested automatically (e.g., `experience.txt`, `skills.txt`, `certifications.txt`, `work history.txt`, `contact information.txt`).
- PDF generation uses WeasyPrint (HTML -> PDF). If WeasyPrint is unavailable or you specify a non-PDF extension, the script writes an `.html` file as a fallback.
- Renderer normalizes list fields and deduplicates projects that duplicate an experience item by title.

Suggested cleanup (optional): Review and delete any unused artifacts in your local clone to keep the repo tidy.
- scripts/.live_runs/ contents are ephemeral outputs produced by scripts.system_live_test; you can safely delete files under this directory at any time.
- data/* sample files can be pruned to only those you actually use; the code simply ingests whatever .txt files are present.
- If you have legacy test files relocated into scripts/ (e.g., an older tests/test_system_scripts_live.py), remove the obsolete copy if it still exists outside scripts/.
