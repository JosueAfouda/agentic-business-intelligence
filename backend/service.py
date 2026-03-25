from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import pandas as pd

from scripts.generate_dataviz import generate_dataviz
from scripts.generate_insights_actions import generate_insights_actions
from scripts.generate_sql import generate_sql
from scripts.run_analysis import execute_analysis
from scripts.run_dataviz import run_dataviz_script
from scripts.schema import generate_schema
from utils.db_discovery import list_databases, list_schemas


REQUESTS_DIR = Path("requests")
SQL_DIR = Path("sql")
DATAVIZ_DIR = Path("dataviz")
OUTPUTS_DIR = Path("outputs")
PROVIDERS = ["gemini", "codex"]


class PipelineServiceError(RuntimeError):
    """Raised when the backend pipeline cannot complete."""


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    normalized = normalized.strip("_")
    return normalized or "analysis"


def capture_step(step_name: str, func: Any, *args: Any, **kwargs: Any) -> str:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            func(*args, **kwargs)
    except SystemExit as exc:
        output = buffer.getvalue().strip()
        message = f"{step_name} failed with exit code {exc.code}."
        if output:
            message = f"{message}\n{output}"
        raise PipelineServiceError(message) from exc
    except Exception as exc:
        output = buffer.getvalue().strip()
        message = f"{step_name} failed: {exc}"
        if output:
            message = f"{message}\n{output}"
        raise PipelineServiceError(message) from exc
    return buffer.getvalue().strip()


def build_question_name(question_text: str, requested_name: str, overwrite_existing: bool) -> str:
    if requested_name.strip():
        question_name = slugify(requested_name)
        request_file = REQUESTS_DIR / f"{question_name}.txt"
        if request_file.exists() and not overwrite_existing:
            raise PipelineServiceError(
                f"The request name '{question_name}' already exists. Enable overwrite or choose another name."
            )
        return question_name

    base_name = slugify(question_text[:80])
    request_file = REQUESTS_DIR / f"{base_name}.txt"
    if not request_file.exists() or overwrite_existing:
        return base_name

    suffix = 2
    while True:
        candidate = f"{base_name}_{suffix}"
        if not (REQUESTS_DIR / f"{candidate}.txt").exists():
            return candidate
        suffix += 1


def write_request_file(question_name: str, question_text: str, overwrite_existing: bool) -> Path:
    REQUESTS_DIR.mkdir(exist_ok=True)
    request_file = REQUESTS_DIR / f"{question_name}.txt"
    if request_file.exists() and not overwrite_existing:
        raise PipelineServiceError(f"Request file already exists: {request_file}")
    request_file.write_text(question_text.strip(), encoding="utf-8")
    return request_file


def validate_file(path: Path, label: str) -> None:
    if not path.exists():
        raise PipelineServiceError(f"{label} was not generated: {path}")
    if path.suffix in {".sql", ".py", ".md", ".html"} and not path.read_text(encoding="utf-8").strip():
        raise PipelineServiceError(f"{label} is empty: {path}")


def dataframe_to_records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    safe_dataframe = dataframe.where(pd.notnull(dataframe), None)
    return safe_dataframe.to_dict(orient="records")


def normalize_dtype(dtype: Any) -> str:
    dtype_name = str(dtype).lower()
    if "int" in dtype_name:
        return "INTEGER"
    if "float" in dtype_name or "double" in dtype_name:
        return "FLOAT"
    if "bool" in dtype_name:
        return "BOOLEAN"
    if "datetime" in dtype_name:
        return "DATETIME"
    return "TEXT"


def build_metadata(
    metadata_path: Path,
    dataframe: pd.DataFrame,
    execution_time_ms: int,
    sql_text: str,
) -> dict[str, Any]:
    raw_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    columns = [
        {"name": column_name, "type": normalize_dtype(dataframe[column_name].dtype)}
        for column_name in dataframe.columns
    ]

    return {
        "question": raw_metadata.get("question"),
        "rows_returned": raw_metadata.get("rows_returned", len(dataframe)),
        "columns": columns,
        "sql_file": raw_metadata.get("sql_file"),
        "database": raw_metadata.get("database"),
        "schema": raw_metadata.get("schema"),
        "execution_time_ms": execution_time_ms,
        "query_hash": hashlib.sha256(sql_text.encode("utf-8")).hexdigest()[:20],
    }


def run_pipeline(
    question_text: str,
    artifact_name: str,
    database_name: str,
    schema_name: str,
    provider_name: str,
    overwrite_existing: bool,
) -> dict[str, Any]:
    if not question_text.strip():
        raise PipelineServiceError("questionText is required.")
    if not database_name.strip():
        raise PipelineServiceError("databaseName is required.")
    if not schema_name.strip():
        raise PipelineServiceError("schemaName is required.")
    if provider_name not in PROVIDERS:
        raise PipelineServiceError(f"Unsupported provider: {provider_name}")

    question_name = build_question_name(question_text, artifact_name, overwrite_existing)
    request_file = write_request_file(question_name, question_text, overwrite_existing)
    sql_file = SQL_DIR / f"{question_name}.sql"
    csv_file = OUTPUTS_DIR / question_name / f"{question_name}.csv"
    metadata_file = OUTPUTS_DIR / question_name / "metadata.json"
    dataviz_file = DATAVIZ_DIR / f"{question_name}.py"
    html_file = OUTPUTS_DIR / question_name / f"{question_name}.html"
    markdown_file = OUTPUTS_DIR / question_name / f"{question_name}.md"

    logs: list[str] = []
    logs.append(capture_step("Schema generation", generate_schema, database_name, schema_name))
    logs.append(capture_step("SQL generation", generate_sql, request_file, database_name, schema_name, provider_name))
    validate_file(sql_file, "SQL file")

    execution_start = time.perf_counter()
    logs.append(capture_step("SQL execution", execute_analysis, sql_file, database_name, schema_name))
    execution_time_ms = int((time.perf_counter() - execution_start) * 1000)

    validate_file(csv_file, "CSV output")
    validate_file(metadata_file, "Metadata file")
    logs.append(capture_step("Dataviz generation", generate_dataviz, request_file, provider_name))
    validate_file(dataviz_file, "Dataviz script")
    logs.append(capture_step("Dataviz execution", run_dataviz_script, dataviz_file))
    validate_file(html_file, "HTML chart")
    logs.append(capture_step("Insights generation", generate_insights_actions, request_file, provider_name))
    validate_file(markdown_file, "Markdown report")

    logs_text = "\n\n".join(log for log in logs if log)
    context_path = OUTPUTS_DIR / question_name / "backend_context.json"
    logs_path = OUTPUTS_DIR / question_name / "logs.txt"
    context_path.write_text(
        json.dumps(
            {
                "provider_name": provider_name,
                "execution_time_ms": execution_time_ms,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    logs_path.write_text(logs_text, encoding="utf-8")

    return load_result(question_name, execution_time_ms, logs_text)


def load_result(
    question_name: str,
    execution_time_ms: int | None = None,
    log_output: str | None = None,
) -> dict[str, Any]:
    request_file = REQUESTS_DIR / f"{question_name}.txt"
    sql_file = SQL_DIR / f"{question_name}.sql"
    csv_file = OUTPUTS_DIR / question_name / f"{question_name}.csv"
    metadata_file = OUTPUTS_DIR / question_name / "metadata.json"
    html_file = OUTPUTS_DIR / question_name / f"{question_name}.html"
    markdown_file = OUTPUTS_DIR / question_name / f"{question_name}.md"
    context_file = OUTPUTS_DIR / question_name / "backend_context.json"
    logs_file = OUTPUTS_DIR / question_name / "logs.txt"

    validate_file(request_file, "Request file")
    validate_file(sql_file, "SQL file")
    validate_file(csv_file, "CSV output")
    validate_file(metadata_file, "Metadata file")
    validate_file(html_file, "HTML chart")
    validate_file(markdown_file, "Markdown report")

    sql_text = sql_file.read_text(encoding="utf-8")
    dataframe = pd.read_csv(csv_file)
    context = {}
    if context_file.exists():
        context = json.loads(context_file.read_text(encoding="utf-8"))

    resolved_execution_time_ms = execution_time_ms
    if resolved_execution_time_ms is None:
        resolved_execution_time_ms = int(context.get("execution_time_ms", 0))

    metadata = build_metadata(metadata_file, dataframe, resolved_execution_time_ms, sql_text)
    html_content = html_file.read_text(encoding="utf-8")
    report_text = markdown_file.read_text(encoding="utf-8")

    timestamp = int(request_file.stat().st_mtime * 1000)
    resolved_logs = log_output
    if resolved_logs is None and logs_file.exists():
        resolved_logs = logs_file.read_text(encoding="utf-8")
    if resolved_logs is None:
        resolved_logs = f"Artifacts loaded from outputs/{question_name}/"

    return {
        "id": question_name,
        "questionName": question_name,
        "questionText": request_file.read_text(encoding="utf-8").strip(),
        "databaseName": metadata["database"],
        "schemaName": metadata["schema"],
        "providerName": context.get("provider_name", "unknown"),
        "sql": sql_text,
        "csvData": dataframe_to_records(dataframe),
        "metadata": metadata,
        "report": report_text,
        "logs": resolved_logs,
        "timestamp": timestamp,
        "chartHtml": html_content,
        "artifactUrls": {
            "sql": f"/api/artifacts/{question_name}/sql",
            "csv": f"/api/artifacts/{question_name}/csv",
            "metadata": f"/api/artifacts/{question_name}/metadata",
            "chart": f"/api/artifacts/{question_name}/chart",
            "report": f"/api/artifacts/{question_name}/report",
            "logs": f"/api/artifacts/{question_name}/logs",
        },
    }


def list_available_results() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for output_dir in sorted(OUTPUTS_DIR.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True):
        if not output_dir.is_dir():
            continue

        question_name = output_dir.name
        request_file = REQUESTS_DIR / f"{question_name}.txt"
        metadata_file = output_dir / "metadata.json"
        if not request_file.exists() or not metadata_file.exists():
            continue

        metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        context_file = output_dir / "backend_context.json"
        context = {}
        if context_file.exists():
            context = json.loads(context_file.read_text(encoding="utf-8"))
        results.append(
            {
                "id": question_name,
                "questionName": question_name,
                "questionText": request_file.read_text(encoding="utf-8").strip(),
                "databaseName": metadata.get("database"),
                "schemaName": metadata.get("schema"),
                "providerName": context.get("provider_name", "unknown"),
                "timestamp": int(request_file.stat().st_mtime * 1000),
            }
        )
    return results


def get_config(database_name: str | None = None) -> dict[str, Any]:
    databases = list_databases()
    selected_database = database_name or (databases[0] if databases else "")
    schemas = list_schemas(selected_database) if selected_database else []
    return {
        "databases": databases,
        "schemas": schemas,
        "providers": PROVIDERS,
        "selectedDatabase": selected_database,
        "selectedSchema": schemas[0] if schemas else "",
        "selectedProvider": PROVIDERS[0],
    }


def get_artifact_path(question_name: str, artifact_type: str) -> tuple[Path, str]:
    artifact_map = {
        "sql": (SQL_DIR / f"{question_name}.sql", "text/sql"),
        "csv": (OUTPUTS_DIR / question_name / f"{question_name}.csv", "text/csv"),
        "metadata": (OUTPUTS_DIR / question_name / "metadata.json", "application/json"),
        "chart": (OUTPUTS_DIR / question_name / f"{question_name}.html", "text/html"),
        "report": (OUTPUTS_DIR / question_name / f"{question_name}.md", "text/markdown"),
        "logs": (OUTPUTS_DIR / question_name / "logs.txt", "text/plain"),
    }
    if artifact_type not in artifact_map:
        raise PipelineServiceError(f"Unsupported artifact type: {artifact_type}")
    return artifact_map[artifact_type]


def default_cors_origins() -> list[str]:
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    additional = os.getenv("FRONTEND_CORS_ORIGINS", "")
    origins = [frontend_origin]
    if additional.strip():
        origins.extend(origin.strip() for origin in additional.split(",") if origin.strip())
    return origins
