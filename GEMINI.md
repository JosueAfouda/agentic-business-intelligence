# GEMINI.md - Agentic Business Intelligence Workflow

This project implements an AI-driven Business Intelligence (BI) workflow that leverages the Gemini CLI to transform natural language business questions into SQL, execute them against a PostgreSQL database, and generate interactive visualizations as well as strategic insights.

## Project Overview
- **Purpose**: Autonomous BI solution for non-technical users to query relational databases (PostgreSQL) using natural language and receive actionable business recommendations.
- **Architecture**: A deterministic pipeline where each step is a single-file processor, orchestrated by a central TUI or manual CLI calls.
- **Key Technologies**: Python 3.10+, PostgreSQL, Gemini CLI, Pandas, Plotly Express, `psycopg2`, `python-dotenv`.

## Workflow Steps
The project follows a linear pipeline:
1.  **Question**: Input stored in `requests/<name>.txt`.
2.  **Schema Context**: Database schema extracted to `schema/<db_name>_schema.md` via `scripts/schema.py`.
3.  **SQL Generation**: `scripts/generate_sql.py` creates `sql/<name>.sql` using Gemini and `scripts/prompt_template.txt`.
4.  **Analysis**: `scripts/run_analysis.py` executes SQL and saves results to `outputs/<name>/<name>.csv` and `metadata.json`.
5.  **Visualization Generation**: `scripts/generate_dataviz.py` creates a Python script in `dataviz/<name>.py`.
6.  **Report Execution**: `scripts/run_dataviz.py` executes the visualization script to produce `outputs/<name>/<name>.html`.
7.  **Insights & Actions**: `scripts/generate_insights_actions.py` analyzes results to produce `outputs/<name>/<name>.md`.

## Building and Running

### Prerequisites
- Python 3 installed.
- PostgreSQL database accessible.
- **Gemini CLI** installed and configured.
- A `.env` file in the root directory:
  ```env
  DB_HOST=localhost
  DB_PORT=5432
  DB_NAME=dvdrental
  DB_USER=your_user
  DB_PASSWORD=your_password
  ```

### Installation
```bash
pip install -r requirements.txt
```

### Orchestrated Execution (Recommended)
The TUI provides a guided experience for the entire workflow:
```bash
python3 scripts/tui2.py
```

### Manual CLI Execution (Expert Mode)
Always use the `-m` flag to run scripts as modules:
```bash
python3 -m scripts.generate_sql --request requests/question_name.txt --database dvdrental
python3 -m scripts.run_analysis --sql sql/question_name.sql --database dvdrental
python3 -m scripts.generate_dataviz --request requests/question_name.txt
python3 -m scripts.run_dataviz --dataviz dataviz/question_name.py
python3 -m scripts.generate_insights_actions --request requests/question_name.txt
```

## Development Conventions
- **Module-based Execution**: Always execute scripts via `python3 -m scripts.<script_name>`.
- **SQL Standards**: 
    - Use PostgreSQL dialect.
    - Use `--` for comments (Avoid `/* */` as it can cause issues in some parsers).
    - Always use clear, business-friendly aliases for columns.
- **Artifact Preservation**: All intermediate files (SQL, CSV, Python scripts) are kept in their respective directories for audit and debugging.
- **Deterministic Naming**: Output files and directories are strictly named after the initial question file name (`<name>`).
- **Prompting**: LLM prompts are externalized in `scripts/prompt_template*.txt` files to allow for easy tuning without code changes.

## Directory Structure
- `requests/`: Natural language business questions (.txt).
- `schema/`: Markdown representations of database schemas.
- `sql/`: Generated SQL queries.
- `dataviz/`: Generated Python scripts for Plotly visualizations.
- `outputs/`: Final artifacts (CSV data, HTML reports, Markdown insights) organized by question name.
- `scripts/`: Core pipeline logic and TUI.
- `utils/`: Database and schema discovery utilities.
