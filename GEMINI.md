# GEMINI.md - Agentic Business Intelligence Workflow

This project implements an AI-driven Business Intelligence (BI) workflow that leverages the Gemini CLI to transform natural language business questions into SQL, execute them against a PostgreSQL database, and generate interactive visualizations as well as strategic insights.

## Project Overview
- **Purpose**: Autonomous BI solution for non-technical users to query relational databases (PostgreSQL) using natural language and receive actionable business recommendations.
- **Architecture**: A deterministic pipeline where each step is a single-file processor, orchestrated by a central TUI or manual CLI calls.
- **Workflow Steps**:
    1.  **Question**: Input stored in `requests/<name>.txt`.
    2.  **Schema Context**: Database schema extracted to `schema/dvdrental_schema.md`.
    3.  **SQL Generation**: `scripts/generate_sql.py` creates `sql/<name>.sql` using Gemini.
    4.  **Analysis**: `scripts/run_analysis.py` executes SQL and saves `outputs/<name>/<name>.csv`.
    5.  **Visualization**: `scripts/generate_dataviz.py` creates `dataviz/<name>.py`.
    6.  **Report**: `scripts/run_dataviz.py` executes the visualization script to produce `outputs/<name>/<name>.html`.
    7.  **Insights & Actions**: `scripts/generate_insights_actions.py` analyzes results to produce `outputs/<name>/<name>.md`.
- **Tech Stack**: Python 3.10+, PostgreSQL, Gemini CLI, Pandas, Plotly Express, `psycopg2`, `python-dotenv`.

## Building and Running

### Prerequisites
- Python 3 installed.
- PostgreSQL database accessible (e.g., `dvdrental`).
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

1.  **Generate SQL**:
    ```bash
    python3 -m scripts.generate_sql --request requests/question_name.txt
    ```
2.  **Run Analysis**:
    ```bash
    python3 -m scripts.run_analysis --sql sql/question_name.sql
    ```
3.  **Generate Dataviz**:
    ```bash
    python3 -m scripts.generate_dataviz --request requests/question_name.txt
    ```
4.  **Run Dataviz**:
    ```bash
    python3 -m scripts.run_dataviz --dataviz dataviz/question_name.py
    ```
5.  **Generate Insights & Actions**:
    ```bash
    python3 -m scripts.generate_insights_actions --request requests/question_name.txt
    ```

## Development Conventions
- **Explicit Processing**: No script performs implicit directory scanning. Every action requires a specific file path argument.
- **Module-based Imports**: Execute via `python3 -m scripts.<script_name>`.
- **Artifact Preservation**: All intermediate files are kept for audit and debugging purposes.
- **Deterministic naming**: Output files and directories are named after the initial question file name.

## Key Files
- `scripts/tui2.py`: Central orchestrator with Insights & Actions integration.
- `scripts/generate_insights_actions.py`: Strategic analysis script.
- `utils/db_utils.py`: Database connection and query execution logic.
- `schema/dvdrental_schema.md`: The primary context provided to Gemini for SQL generation.
