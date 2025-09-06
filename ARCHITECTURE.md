Architecture Plan

Goals
- Assemble a tailored resume PDF from a job posting URL and a local data directory of source texts.
- Provide a per-file review utility that suggests improvements.
- Use LangChain with Ollama (Docker) as the LLM backend.

Modules and Responsibilities

1) resume_builder.config
   - Centralizes configuration (Ollama base URL, model, temperature) with .env/environment overrides.

2) resume_builder.llm.ollama_client
   - get_ollama_chat(model, temperature) -> LangChain ChatOllama instance.
   - Hides LangChain/Ollama wiring.

3) resume_builder.io
   - job_fetcher.fetch_job_text(url): HTTP GET + BeautifulSoup scraping to extract the main job text, with cleaning.
   - data_loader.load_data_dir(path): Read all .txt files; returns {stem: text} mapping for prompts.

4) resume_builder.prompts.templates
   - Prompt texts for system/human messages:
     - TAILORING_* for building a targeted resume in JSON shape.
     - REVIEW_* for critiquing individual data files.

5) resume_builder.chains
   - tailor_resume.tailor_resume_json(job_text, sources, model, temperature):
     - Composes a LangChain prompt + Ollama chat model + output parser.
     - Ensures output is valid JSON (simple fallback extraction included).
   - review_file.review_source_file(name, content, ...): returns suggestion text.

6) resume_builder.render.pdf
   - render_resume_pdf(data, out_path): Renders an HTML resume via Jinja2 and outputs PDF via WeasyPrint when available; otherwise writes .html.
   - Expected schema: keys summary(str), skills(list), experience(list), projects(list), education(list), extras(list), optional name(str).

7) scripts
   - fetch_job_and_build_resume.py
     - CLI: --url, --data-dir, --out, --model, --temperature
     - Flow: fetch job -> load sources -> LLM tailor -> render PDF/HTML -> save raw JSON next to output.
   - review_data_files.py
     - CLI: --data-dir, --out, --model, --temperature
     - Flow: load sources -> LLM critique per file -> write suggestions.md

Data Expectations
- data/*.txt: arbitrary text per topic. Example files: projects.txt, transcript.txt. You can add skills.txt, experience.txt, achievements.txt, certifications.txt, name.txt (for display name), etc.

Extensibility
- Add more sophisticated parsers (e.g., transcript parser to derive education bullets).
- Add structured templates and stronger JSON schemas (pydantic) for validation.
- Add vector retrieval (FAISS) if data grows large; current design relies on direct concatenation.

Ollama Notes
- Ensure Ollama HTTP API is reachable (default http://localhost:11434) and model is pulled (e.g., `ollama pull llama3`).
- Adjust temperature in CLI or .env for deterministic outputs when needed.
