# Agentic Business Intelligence Engine (Docker)

This document provides instructions for deploying and using the Agentic Business Intelligence Engine via Docker. This solution allows you to transform natural language business questions into actionable insights, visualizations, and strategic recommendations, without needing Python or Gemini CLI installed directly on your machine.

## Overview

The Agentic Business Intelligence Engine uses AI to interact with your PostgreSQL database, generating SQL queries, executing them, and producing interactive data visualizations and business insights. All within a self-contained Docker environment.

## Prerequisites

To run this solution, you only need to have Docker installed on your system.

*   [Install Docker](https://docs.docker.com/get-docker/)

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-repo/agentic-business-intelligence.git
    cd agentic-business-intelligence
    ```
    *(Note: Replace `https://github.com/your-repo/agentic-business-intelligence.git` with the actual repository URL.)*

2.  **Create a `.env` file:**
    Create a file named `.env` in the root directory of the project. This file will contain your PostgreSQL database connection details.

    **Example `.env` file:**
    ```env
    DB_HOST=your_db_host
    DB_PORT=5432
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    # Optional: Enable SSL for database connection (e.g., require, verify-full, disable)
    # DB_SSLMODE=require
    ```
    Replace the placeholder values with your actual PostgreSQL database credentials.

## Usage

All interactions with the Agentic Business Intelligence Engine are done through a single Docker command.

### 1. Running the Interactive TUI (Default)

The primary way to use the engine is through its interactive Text User Interface (TUI). This will guide you through the entire workflow.

```bash
docker compose run --rm agentic-bi
```

*   **First Run - Gemini Authentication:**
    The very first time you run this command, the Gemini CLI embedded within the container will prompt you to authenticate with your Google account. Follow the instructions in your terminal to complete the OAuth login process. This authentication state will be securely persisted on your local machine across runs.

*   **Subsequent Runs:**
    On subsequent runs, if authentication is still valid, the TUI will launch directly, allowing you to select your database, schema, and input your business questions.

### 2. Running CLI Commands

You can also execute specific CLI commands within the container for more advanced use cases or automation. Simply append the desired command after `docker compose run --rm agentic-bi`.

**Examples:**

*   **Get help for Gemini CLI:**
    ```bash
    docker compose run --rm agentic-bi gemini --help
    ```

*   **Generate SQL for a specific request:**
    ```bash
    docker compose run --rm agentic-bi python3 -m scripts.generate_sql --request requests/my_question.txt --database my_db --schema public
    ```
    *(Note: Ensure `requests/my_question.txt` exists on your host machine in the `requests` directory.)*

## Data Persistence

All generated artifacts (SQL files, schema definitions, data visualizations, insights, and raw output data) as well as your Gemini authentication state are persisted to your local filesystem.

*   **Application Data:**
    *   `requests/` (input questions)
    *   `sql/` (generated SQL queries)
    *   `schema/` (database schema markdown)
    *   `dataviz/` (generated Python visualization scripts)
    *   `outputs/` (CSV data, HTML reports, Markdown insights)

*   **Gemini Authentication:**
    Your Gemini authentication tokens are stored persistently in a Docker volume, meaning you only need to authenticate once.

## Security Note

The application's source code is encapsulated within the Docker container and is not exposed to your host machine.

---
