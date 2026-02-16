# GEMINI.md - Agent-centric Business Intelligence Workflow

This project implements an **Agent-centric Business Intelligence (BI)** workflow that leverages the Gemini CLI to transform natural language business questions into actionable insights. It automates the process of SQL generation, data extraction, and visualization.

## Project Overview

- **Purpose**: To provide a low-cost, transparent, and auditable BI solution for SMEs and startups, allowing non-technical users to query databases using natural language.
- **Core Workflow**:
    1.  **Question**: Users place `.txt` files in `requests/`.
    2.  **Schema**: Database schema is extracted and stored in `schema/dvdrental_schema.md`.
    3.  **SQL Generation**: `scripts/generate_sql.py` calls Gemini to generate SQL based on the question and schema.
    4.  **Analysis**: `scripts/run_analysis.py` executes the SQL against a PostgreSQL database and exports results to `outputs/`.
    5.  **Visualization**: `scripts/generate_dataviz.py` creates Plotly-based Python scripts in `dataviz/`, which are then executed by `scripts/run_dataviz.py` to produce HTML reports.
- **Main Technologies**: Python 3, PostgreSQL, Gemini CLI, Pandas, Plotly Express, `psycopg2`.

## Building and Running

### Prerequisites
- Python 3.x installed.
- PostgreSQL database (e.g., the `dvdrental` sample database).
- **Gemini CLI** installed and configured in your environment.
- Environment variables set in a `.env` file:
  ```env
  DB_HOST=your_host
  DB_PORT=5432
  DB_NAME=dvdrental
  DB_USER=your_user
  DB_PASSWORD=your_password
  ```

### Key Commands
- **Install Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
- **Full Workflow (TUI)**:
  ```bash
  python scripts/tui.py
  ```
- **Individual Steps**:
    - **Update Schema**: `python3 scripts/schema.py`
    - **Generate SQL**: `python3 scripts/generate_sql.py`
    - **Run Analysis**: `python3 scripts/run_analysis.py`
    - **Generate Dataviz**: `python3 scripts/generate_dataviz.py`
    - **Run Dataviz**: `python3 scripts/run_dataviz.py`

## Directory Structure
- `requests/`: Input natural language questions (`.txt`).
- `sql/`: Generated SQL queries.
- `schema/`: Database schema documentation.
- `outputs/`: CSV results and `metadata.json` for each question.
- `dataviz/`: Generated Python scripts for data visualization.
- `scripts/`: Core execution logic and TUI.
- `utils/`: Shared utilities (e.g., database connection).

## Development Conventions
- **Incremental-Safe**: Scripts are designed to skip already processed items (e.g., won't regenerate SQL if it already exists) to prevent accidental overwrites and save tokens/time.
- **Auditability**: Every step produces a tangible artifact (SQL file, CSV, metadata, HTML) for transparency.
- **Modular Design**: Database logic is isolated in `utils/db_utils.py`, making it easier to extend to other SGBDRs (MySQL, SQL Server) in the future.
- **Clean SQL**: The system expects clean SQL for direct execution via `psycopg2`.
