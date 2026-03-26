# Repository Guidelines

## Project Structure & Module Organization
The core BI pipeline lives in `scripts/` and is designed to be run as modules, for example `python -m scripts.tui2` or `python -m scripts.generate_sql`. Database helpers live in `utils/`. LLM provider adapters live in `llm/`. Generated workflow artifacts should stay aligned by business question across `requests/`, `sql/`, `schema/`, `dataviz/`, and `outputs/`:

`requests/top_movies.txt` -> `sql/top_movies.sql` -> `outputs/top_movies/`

The web stack is split between `backend/` for the FastAPI service and `frontend/` for the React + Vite UI. Root infrastructure files include `requirements.txt`, `Dockerfile`, `docker-compose.yml`, and `README.md`.

## Build, Test, and Development Commands
Create a local environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the recommended text workflow:

```bash
python -m scripts.tui2
python -m scripts.tui2 --provider codex
```

Run individual pipeline stages when debugging:

```bash
python -m scripts.schema --database dvdrental --schema public
python -m scripts.generate_sql --request requests/top_movies.txt --database dvdrental --schema public
python -m scripts.run_analysis --sql sql/top_movies.sql --database dvdrental --schema public
```

Use `docker compose run --rm agentic-bi` for a containerized run.

## Coding Style & Naming Conventions
Use Python with 4-space indentation, `snake_case` for files, functions, and variables, and `Path`-based file handling where practical. Keep modules focused and CLI arguments explicit. Name generated artifacts with business-readable slugs such as `top_movies_by_revenue`. Follow the existing pattern of small scripts rather than large multi-purpose modules.

## Testing Guidelines
There is no dedicated `tests/` suite yet. Validate changes with targeted smoke runs of the affected script and at least one end-to-end sample flow when behavior changes. Check generated files under `outputs/<question_name>/` and confirm the matching SQL, CSV, HTML, or Markdown artifacts look correct.

## Commit & Pull Request Guidelines
Recent history mixes short lowercase subjects (`readme final`) with concise feature-style messages (`feat: add Codex support alongside Gemini CLI`). Keep commits focused, imperative, and scoped to one logical change. PRs should state the workflow touched, required `.env` or database assumptions, and include sample output paths or screenshots for TUI or frontend changes.

## Security & Configuration Tips
Keep secrets in a local `.env` and never commit credentials or customer data. Treat files in `outputs/` as potentially sensitive and sanitize examples before sharing them externally.
