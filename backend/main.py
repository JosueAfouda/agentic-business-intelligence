from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from backend.service import (
    clear_history,
    PipelineServiceError,
    default_cors_origins,
    get_artifact_path,
    get_config,
    list_available_results,
    load_result,
    run_pipeline,
)


app = FastAPI(
    title="Agentic BI API",
    version="0.1.0",
    description="Backend API for the React Agentic BI frontend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/config")
def config(database_name: str | None = Query(default=None, alias="databaseName")) -> dict:
    try:
        return get_config(database_name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/databases")
def databases() -> dict:
    try:
        config_data = get_config()
        return {"databases": config_data["databases"]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/databases/{database_name}/schemas")
def schemas(database_name: str) -> dict:
    try:
        config_data = get_config(database_name)
        return {"schemas": config_data["schemas"]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/providers")
def providers() -> dict:
    return {"providers": ["gemini", "codex"]}


@app.get("/api/results")
def results() -> dict:
    return {"history": list_available_results()}


@app.delete("/history")
@app.delete("/api/history")
def delete_history() -> dict[str, str]:
    try:
        return clear_history()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/results/{question_name}")
def result_detail(question_name: str) -> dict:
    try:
        return load_result(question_name)
    except PipelineServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/pipeline/run")
def pipeline_run(payload: dict) -> dict:
    try:
        return run_pipeline(
            question_text=str(payload.get("questionText", "")).strip(),
            artifact_name=str(payload.get("artifactName", "")),
            database_name=str(payload.get("databaseName", "")),
            schema_name=str(payload.get("schemaName", "")),
            provider_name=str(payload.get("providerName", "gemini")),
            overwrite_existing=bool(payload.get("overwriteExisting", False)),
        )
    except PipelineServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/artifacts/{question_name}/{artifact_type}")
def artifact(question_name: str, artifact_type: str):
    try:
        artifact_path, media_type = get_artifact_path(question_name, artifact_type)
    except PipelineServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if artifact_type == "logs":
        result = load_result(question_name)
        return PlainTextResponse(result["logs"], media_type=media_type)

    if not artifact_path.exists():
        raise HTTPException(status_code=404, detail=f"Artifact not found: {artifact_path}")

    if artifact_type == "metadata":
        result = load_result(question_name)
        return JSONResponse(result["metadata"])

    return FileResponse(artifact_path, media_type=media_type, filename=artifact_path.name)
