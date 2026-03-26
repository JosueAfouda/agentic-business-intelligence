# Repository Guidelines

## Project Structure & Module Organization
`scripts/` contains the pipeline entrypoints (`schema`, `generate_sql`, `run_analysis`, `generate_dataviz`, `run_dataviz`, `generate_insights_actions`, `tui2`). `utils/` holds PostgreSQL connection and discovery helpers. `requests/`, `sql/`, `schema/`, `dataviz/`, and `outputs/` store generated workflow artifacts; keep names aligned across these folders, for example `requests/top_movies.txt` -> `sql/top_movies.sql` -> `outputs/top_movies/`. Root files include `requirements.txt`, `Dockerfile`, `docker-compose.yml`, and [README.md](/home/vant/Documents/business/agentic-business-intelligence/README.md).

## Build, Test, and Development Commands
Create a virtualenv and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Run the guided workflow:
```bash
python -m scripts.tui2
```
Run the pipeline manually:
```bash
python -m scripts.schema --database dvdrental --schema public
python -m scripts.generate_sql --request requests/top_movies.txt --database dvdrental --schema public
python -m scripts.run_analysis --sql sql/top_movies.sql --database dvdrental --schema public
python -m scripts.generate_dataviz --request requests/top_movies.txt
python -m scripts.run_dataviz --dataviz dataviz/top_movies.py
python -m scripts.generate_insights_actions --request requests/top_movies.txt
```
Docker is available for the same TUI flow with `docker compose run --rm agentic-bi`.

## Coding Style & Naming Conventions
Use Python with 4-space indentation, `snake_case` for files, functions, and variables, and `Path`-based file handling where possible. Run scripts as modules (`python -m scripts.<name>`) rather than by file path. Follow existing conventions: small single-purpose modules, explicit CLI arguments, and business-readable artifact names such as `top_movies_by_revenue`.

## Testing Guidelines
There is no dedicated `tests/` suite yet. Validate changes with targeted smoke runs of the affected module and verify generated outputs under `outputs/<question_name>/`. For safe checks, prefer `python -m scripts.schema ...` and one end-to-end sample workflow before opening a PR.

## Commit & Pull Request Guidelines
Recent history uses short, lowercase commit subjects such as `readme final` and `add choose schema option OK`. Keep commits focused, imperative, and concise; one logical change per commit. PRs should include the workflow or module touched, required `.env` or database assumptions, and sample output paths or screenshots when TUI/dataviz behavior changes.

## Security & Configuration Tips
Keep credentials in a local `.env`; do not commit secrets or customer data exports. Generated CSV/HTML/Markdown files in `outputs/` may contain sensitive data, so sanitize examples before sharing them.
