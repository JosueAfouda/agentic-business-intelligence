# Agentic Business Intelligence Workflow

This project implements an AI-driven Business Intelligence (BI) workflow that transforms natural language business questions into executable SQL queries, runs them against a PostgreSQL database, and exports the results for analysis.

## Project Overview
The workflow uses Gemini to bridge the gap between business intent and technical execution. It is designed to be incremental, auditable, and easy to use for non-technical stakeholders or developers looking to automate data extraction.

### Core Technologies
- **LLM:** Gemini (via Gemini CLI)
- **Database:** PostgreSQL
- **Language:** Python 3
- **Libraries:** `psycopg2`, `pandas`, `python-dotenv`

---

## Architecture
The workflow follows a 4-step pipeline:
1. **Schema Extraction:** `scripts/schema.py` reads the database structure and generates a markdown representation.
2. **SQL Generation:** `scripts/generate_sql.py` takes a natural language question and the schema to generate a PostgreSQL query via Gemini.
3. **Execution:** `scripts/run_analysis.py` executes the generated SQL and saves the results.
4. **Export:** Results are stored as CSV files along with a `metadata.json` for traceability.

---

## Setup and Configuration

### Prerequisites
- Python 3.x installed.
- Gemini CLI installed and configured.
- A PostgreSQL database (e.g., `dvdrental`).

### Installation
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
DB_HOST=your_host
DB_PORT=5432
DB_NAME=dvdrental
DB_USER=your_user
DB_PASSWORD=your_password
```

---

## Usage

### 1. Update the Database Schema
If the database structure changes, regenerate the schema context:
```bash
python scripts/schema.py
```

### 2. Add a Business Question
Create a new `.txt` file in the `requests/` directory (e.g., `requests/top_customers.txt`) with your question in plain language.

### 3. Generate SQL Queries
Convert all new requests into SQL files:
```bash
python scripts/generate_sql.py
```
Generated SQL will be stored in `sql/*.sql`.

### 4. Run Analysis
Execute all new SQL queries and generate CSV reports:
```bash
python scripts/run_analysis.py
```
Outputs will be available in `outputs/<question_name>/`.

---

## Project Structure
- `requests/`: Input natural language questions (.txt).
- `sql/`: AI-generated PostgreSQL queries (.sql).
- `outputs/`: Final results containing CSV data and `metadata.json`.
- `schema/`: Documentation of the database schema used as context for the LLM.
- `scripts/`: Automation scripts for the BI pipeline.
- `utils/`: Shared utilities for database connection and query execution.

---

## Development Conventions
- **Incremental Processing:** Scripts are designed to skip already processed files (e.g., won't regenerate SQL if it exists, won't rerun query if CSV exists).
- **PostgreSQL Focus:** All logic and prompt templates are optimized for PostgreSQL syntax.
- **Auditability:** Every output is paired with its originating SQL and metadata to ensure results can be verified by human analysts.
