from __future__ import annotations

import contextlib
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from streamlit.components.v1 import html

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


@dataclass
class PipelineResult:
    question_name: str
    question_text: str
    database_name: str
    schema_name: str
    request_file: Path
    sql_file: Path
    csv_file: Path
    metadata_file: Path
    dataviz_file: Path
    html_file: Path
    markdown_file: Path
    log_output: str

    @property
    def label(self) -> str:
        return f"{self.question_name} [{self.database_name}.{self.schema_name}]"


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    normalized = normalized.strip("_")
    return normalized or "analysis"


def ensure_session_state() -> None:
    if "history" not in st.session_state:
        st.session_state.history = []
    if "selected_history" not in st.session_state:
        st.session_state.selected_history = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


@st.cache_data(show_spinner=False)
def load_databases() -> list[str]:
    return list_databases()


@st.cache_data(show_spinner=False)
def load_schemas(database_name: str) -> list[str]:
    return list_schemas(database_name)


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
        raise RuntimeError(message) from exc
    except Exception as exc:
        output = buffer.getvalue().strip()
        message = f"{step_name} failed: {exc}"
        if output:
            message = f"{message}\n{output}"
        raise RuntimeError(message) from exc
    return buffer.getvalue().strip()


def add_history_entry(result: PipelineResult) -> None:
    history = st.session_state.history
    history = [entry for entry in history if entry["question_name"] != result.question_name]
    history.insert(
        0,
        {
            "question_name": result.question_name,
            "question_text": result.question_text,
            "database_name": result.database_name,
            "schema_name": result.schema_name,
        },
    )
    st.session_state.history = history[:10]


def build_question_name(question_text: str, requested_name: str, overwrite_existing: bool) -> str:
    if requested_name.strip():
        question_name = slugify(requested_name)
        request_file = REQUESTS_DIR / f"{question_name}.txt"
        if request_file.exists() and not overwrite_existing:
            raise FileExistsError(
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
        raise FileExistsError(f"Request file already exists: {request_file}")
    request_file.write_text(question_text.strip(), encoding="utf-8")
    return request_file


def validate_file(path: Path, label: str) -> None:
    if not path.exists():
        raise RuntimeError(f"{label} was not generated: {path}")
    if path.suffix in {".sql", ".py", ".md"} and not path.read_text(encoding="utf-8").strip():
        raise RuntimeError(f"{label} is empty: {path}")


def run_pipeline(
    question_text: str,
    requested_name: str,
    database_name: str,
    schema_name: str,
    overwrite_existing: bool,
) -> PipelineResult:
    question_name = build_question_name(question_text, requested_name, overwrite_existing)
    request_file = write_request_file(question_name, question_text, overwrite_existing)
    sql_file = SQL_DIR / f"{question_name}.sql"
    csv_file = OUTPUTS_DIR / question_name / f"{question_name}.csv"
    metadata_file = OUTPUTS_DIR / question_name / "metadata.json"
    dataviz_file = DATAVIZ_DIR / f"{question_name}.py"
    html_file = OUTPUTS_DIR / question_name / f"{question_name}.html"
    markdown_file = OUTPUTS_DIR / question_name / f"{question_name}.md"

    logs: list[str] = []
    logs.append(capture_step("Schema generation", generate_schema, database_name, schema_name))
    logs.append(capture_step("SQL generation", generate_sql, request_file, database_name, schema_name))
    validate_file(sql_file, "SQL file")
    logs.append(capture_step("SQL execution", execute_analysis, sql_file, database_name, schema_name))
    validate_file(csv_file, "CSV output")
    validate_file(metadata_file, "Metadata file")
    logs.append(capture_step("Dataviz generation", generate_dataviz, request_file))
    validate_file(dataviz_file, "Dataviz script")
    logs.append(capture_step("Dataviz execution", run_dataviz_script, dataviz_file))
    validate_file(html_file, "HTML chart")
    logs.append(capture_step("Insights generation", generate_insights_actions, request_file))
    validate_file(markdown_file, "Markdown report")

    return PipelineResult(
        question_name=question_name,
        question_text=question_text.strip(),
        database_name=database_name,
        schema_name=schema_name,
        request_file=request_file,
        sql_file=sql_file,
        csv_file=csv_file,
        metadata_file=metadata_file,
        dataviz_file=dataviz_file,
        html_file=html_file,
        markdown_file=markdown_file,
        log_output="\n\n".join(log for log in logs if log),
    )


def result_from_history(entry: dict[str, str]) -> PipelineResult:
    question_name = entry["question_name"]
    return PipelineResult(
        question_name=question_name,
        question_text=entry["question_text"],
        database_name=entry["database_name"],
        schema_name=entry["schema_name"],
        request_file=REQUESTS_DIR / f"{question_name}.txt",
        sql_file=SQL_DIR / f"{question_name}.sql",
        csv_file=OUTPUTS_DIR / question_name / f"{question_name}.csv",
        metadata_file=OUTPUTS_DIR / question_name / "metadata.json",
        dataviz_file=DATAVIZ_DIR / f"{question_name}.py",
        html_file=OUTPUTS_DIR / question_name / f"{question_name}.html",
        markdown_file=OUTPUTS_DIR / question_name / f"{question_name}.md",
        log_output="History item loaded from generated artifacts.",
    )


def load_dataframe(csv_file: Path) -> pd.DataFrame:
    return pd.read_csv(csv_file)


def render_message(role: str, content: str) -> None:
    role_class = "user" if role == "user" else "assistant"
    st.markdown(
        f"""
        <div class="chat-row {role_class}">
            <div class="chat-bubble {role_class}">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(result: PipelineResult) -> None:
    validate_file(result.sql_file, "SQL file")
    validate_file(result.csv_file, "CSV output")
    validate_file(result.metadata_file, "Metadata file")
    validate_file(result.html_file, "HTML chart")
    validate_file(result.markdown_file, "Markdown report")

    sql_text = result.sql_file.read_text(encoding="utf-8")
    metadata = json.loads(result.metadata_file.read_text(encoding="utf-8"))
    markdown_report = result.markdown_file.read_text(encoding="utf-8")
    html_content = result.html_file.read_text(encoding="utf-8")
    dataframe = load_dataframe(result.csv_file)

    render_message("user", result.question_text)
    render_message(
        "assistant",
        (
            f"Pipeline executed on <strong>{result.database_name}.{result.schema_name}</strong>.<br>"
            f"Artifacts available in <code>outputs/{result.question_name}/</code>."
        ),
    )

    tab_sql, tab_table, tab_meta, tab_chart, tab_report, tab_logs = st.tabs(
        ["SQL", "Results", "Metadata", "Chart", "Report", "Logs"]
    )

    with tab_sql:
        st.download_button(
            "Download SQL",
            data=sql_text,
            file_name=result.sql_file.name,
            mime="text/sql",
            use_container_width=True,
        )
        st.code(sql_text, language="sql")

    with tab_table:
        st.download_button(
            "Download CSV",
            data=result.csv_file.read_bytes(),
            file_name=result.csv_file.name,
            mime="text/csv",
            use_container_width=True,
        )
        st.dataframe(dataframe, use_container_width=True, hide_index=True)

    with tab_meta:
        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.download_button(
                "Download metadata",
                data=json.dumps(metadata, indent=2),
                file_name=result.metadata_file.name,
                mime="application/json",
                use_container_width=True,
            )
            st.json(metadata)
        with col_right:
            profile_rows = len(dataframe)
            profile_cols = len(dataframe.columns)
            st.metric("Rows", profile_rows)
            st.metric("Columns", profile_cols)
            st.dataframe(
                pd.DataFrame(
                    {
                        "column": dataframe.columns,
                        "dtype": [str(dtype) for dtype in dataframe.dtypes],
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            numeric_df = dataframe.select_dtypes(include="number")
            if not numeric_df.empty:
                st.caption("Numeric summary")
                st.dataframe(numeric_df.describe().transpose(), use_container_width=True)

    with tab_chart:
        st.download_button(
            "Download chart HTML",
            data=html_content,
            file_name=result.html_file.name,
            mime="text/html",
            use_container_width=True,
        )
        html(html_content, height=560, scrolling=True)

    with tab_report:
        st.download_button(
            "Download report",
            data=markdown_report,
            file_name=result.markdown_file.name,
            mime="text/markdown",
            use_container_width=True,
        )
        st.markdown(markdown_report)

    with tab_logs:
        st.code(result.log_output or "No execution logs captured.", language="text")


def configure_page() -> None:
    st.set_page_config(
        page_title="Agentic BI",
        page_icon=":bar_chart:",
        layout="wide",
    )
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(16, 185, 129, 0.10), transparent 28%),
                linear-gradient(180deg, #f5f1e8 0%, #fbfaf6 45%, #f3efe6 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        .hero {
            padding: 1.2rem 1.4rem;
            border: 1px solid rgba(18, 39, 32, 0.12);
            border-radius: 22px;
            background: rgba(255, 252, 247, 0.92);
            box-shadow: 0 18px 45px rgba(64, 55, 32, 0.08);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2rem;
            color: #17261d;
        }
        .hero p {
            margin: 0.35rem 0 0;
            color: #4f5b53;
            font-size: 1rem;
        }
        .chat-row {
            display: flex;
            margin: 0.6rem 0;
        }
        .chat-row.user {
            justify-content: flex-end;
        }
        .chat-row.assistant {
            justify-content: flex-start;
        }
        .chat-bubble {
            max-width: 78%;
            padding: 0.95rem 1rem;
            border-radius: 18px;
            line-height: 1.45;
            box-shadow: 0 10px 25px rgba(36, 36, 36, 0.06);
        }
        .chat-bubble.user {
            background: #173f35;
            color: #f7f7f4;
        }
        .chat-bubble.assistant {
            background: #fffdf8;
            color: #1f2a22;
            border: 1px solid rgba(23, 63, 53, 0.15);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    configure_page()
    ensure_session_state()

    st.markdown(
        """
        <div class="hero">
            <h1>Agentic BI Streamlit</h1>
            <p>Question métier → SQL → exécution → dataviz → insights, sans modifier le pipeline existant.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.subheader("Configuration")
        if st.button("Refresh databases", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        databases = load_databases()
        if not databases:
            st.error("No PostgreSQL database was discovered. Check `.env` and server access.")
            st.stop()

        database_name = st.selectbox("Database", databases, index=0)

        schemas = load_schemas(database_name)
        if not schemas:
            st.error(f"No usable schema found in database '{database_name}'.")
            st.stop()

        schema_name = st.selectbox("Schema", schemas, index=0)
        overwrite_existing = st.checkbox("Overwrite existing artifacts", value=False)

        st.divider()
        st.subheader("History")
        history = st.session_state.history
        if history:
            labels = [f"{item['question_name']} [{item['database_name']}.{item['schema_name']}]" for item in history]
            selected_label = st.selectbox(
                "Previous runs",
                options=["Current session result"] + labels,
                index=0,
            )
            if selected_label != "Current session result":
                selected_index = labels.index(selected_label)
                st.session_state.selected_history = history[selected_index]
            else:
                st.session_state.selected_history = None
        else:
            st.caption("No previous Streamlit runs in this session.")

        st.divider()
        st.caption("Prerequisites: `.env` configured, PostgreSQL reachable, Gemini CLI installed.")

    with st.form("question_form", clear_on_submit=False):
        question_text = st.text_area(
            "Business question",
            placeholder="Ex: Quels sont les 5 films ayant généré le plus de revenus ?",
            height=120,
        )
        requested_name = st.text_input(
            "Artifact name",
            placeholder="Optional. Example: top_movies_by_revenue",
            help="If empty, a name is generated from the question.",
        )
        submit = st.form_submit_button("Ask", use_container_width=True)

    if submit:
        if not question_text.strip():
            st.error("Please enter a business question before running the pipeline.")
        else:
            try:
                with st.spinner("Running the existing Agentic BI pipeline..."):
                    result = run_pipeline(
                        question_text=question_text,
                        requested_name=requested_name,
                        database_name=database_name,
                        schema_name=schema_name,
                        overwrite_existing=overwrite_existing,
                    )
                st.session_state.last_result = result
                st.session_state.selected_history = None
                add_history_entry(result)
                st.success(f"Workflow completed for '{result.question_name}'.")
            except Exception as exc:
                st.error(str(exc))

    active_result = st.session_state.last_result
    if st.session_state.selected_history is not None:
        try:
            active_result = result_from_history(st.session_state.selected_history)
        except Exception as exc:
            st.error(f"Unable to load history item: {exc}")

    if active_result is not None:
        try:
            render_result(active_result)
        except Exception as exc:
            st.error(f"Unable to render artifacts: {exc}")
    else:
        st.info("Select a database/schema, enter a business question, and run the pipeline.")


if __name__ == "__main__":
    main()
