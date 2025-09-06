# Resume Builder (LangChain + Ollama)

This project focuses on a rewrite-only pipeline that builds a YAML resume from a job posting and your local `data/` directory. Ollama (local LLM server) is used via LangChain.

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
    - loader.py
    - text/
      - clean_job_description.txt
      - shorten_file.txt
      - build_yaml_resume.txt
  - chains/
    - __init__.py
    - rewrite_pipeline.py
- scripts/
  - rewrite_fetch_job_and_build_yaml_resume.py

## Installation

1) Create/activate a virtual environment and install dependencies:

```
pip install -r requirements.txt
```

Key dependencies include: langchain-ollama, requests, beautifulsoup4, pydantic, python-dotenv. The LangChain integration is provided via the `langchain-ollama` package.

2) Ensure Ollama is running and exposes its HTTP API (default http://localhost:11434). Install desired models (e.g., `llama3`, `mistral`, or your preferred compatible model):

```
ollama pull llama3
```

## Usage

- Rewrite pipeline: Build a YAML resume via staged LLM prompts (clean -> shorten -> YAML). It prints a status message before each LLM call, and logs every LLM output to a file.

```
python -m scripts.rewrite_fetch_job_and_build_yaml_resume \
  --job-url "https://example.com/jobs/123" \
  --data-dir ./data \
  --out ./resume.yaml \
  --model gpt-oss \
  --temperature 0.2 \
  --log-file ./resume.yaml.llm.log  # optional; by default logs next to --out as <out>.llm.log
```

Logging:
- Every LLM output (cleaned description, each per-file shortening, final YAML) is appended to the log file.
- Default log path: if --log-file is not provided, it will write to <out>.llm.log next to your --out.

Alternative inputs:
- --job-file ./job_posting.txt
- --job-text "paste raw job text here"

What happens:
- Raw job description is fetched (if URL) and cleaned (boilerplate removed, high-signal kept).
- Each .txt data file is shortened to up to 5 bullets relevant to the job.
- A YAML resume matching yamlresume schema is produced, with instruction to reorder and trim to fit.
- Prompts used for each stage live at resume_builder/prompts/text/*.txt.

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

## Notes

- Ensure Ollama HTTP API is reachable (default http://localhost:11434) and that your chosen model is pulled locally.
- Be mindful of sensitive information in prompts when sharing logs; the rewrite script logs all LLM outputs to a file.

## Maintenance notes

- All `.txt` files in `data/` are ingested automatically (e.g., `experience.txt`, `skills.txt`, `certifications.txt`, `work history.txt`, `contact information.txt`).
- Suggested cleanup: prune data/* samples you don’t use; the code ingests whatever .txt files are present.
