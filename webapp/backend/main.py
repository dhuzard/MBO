from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from .exporter import export_to_file, export_ttl
from .ontology import OntologyService
from .schemas import (
    BehaviorClassResponse,
    BehaviorRequest,
    BehaviorResponse,
    ExportResponse,
    PrefixUpdate,
    ValidationResponse,
)
from .storage import WorkspaceStorage
from .validation import run_shacl_validation


app = FastAPI(title="MBO Behavior Builder", version="0.1.0")

ontology_service = OntologyService()
workspace_storage = WorkspaceStorage()

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.get("/", include_in_schema=False)
def redirect_to_frontend() -> RedirectResponse:
    return RedirectResponse(url="/app/")


@app.get("/api/behavior-classes", response_model=List[BehaviorClassResponse])
def list_behavior_classes() -> List[BehaviorClassResponse]:
    classes = ontology_service.list_behavior_classes()
    return [
        BehaviorClassResponse(
            iri=entry.iri,
            label=entry.label,
            comment=entry.comment,
            description=entry.description,
            parents=entry.parents,
            category=entry.category,
        )
        for entry in classes
    ]


@app.get("/api/prefixes")
def list_prefixes():
    return workspace_storage.prefixes


@app.post("/api/prefixes", status_code=204)
def set_prefix(payload: PrefixUpdate) -> None:
    try:
        workspace_storage.set_prefix(payload.prefix, payload.iri)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.delete("/api/prefixes/{prefix}", status_code=204)
def remove_prefix(prefix: str) -> None:
    try:
        workspace_storage.remove_prefix(prefix)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/behaviors", response_model=List[BehaviorResponse])
def list_behaviors() -> List[BehaviorResponse]:
    return [BehaviorResponse(**entry.__dict__) for entry in workspace_storage.list_behaviors()]


@app.post("/api/behaviors", response_model=BehaviorResponse, status_code=201)
def create_behavior(payload: BehaviorRequest) -> BehaviorResponse:
    entry = workspace_storage.upsert_behavior(uid=None, **payload.dict())
    return BehaviorResponse(**entry.__dict__)


@app.put("/api/behaviors/{uid}", response_model=BehaviorResponse)
def update_behavior(uid: str, payload: BehaviorRequest) -> BehaviorResponse:
    try:
        entry = workspace_storage.upsert_behavior(uid=uid, **payload.dict())
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return BehaviorResponse(**entry.__dict__)


@app.delete("/api/behaviors/{uid}", status_code=204)
def delete_behavior(uid: str) -> None:
    try:
        workspace_storage.delete_behavior(uid)
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/validate", response_model=ValidationResponse)
def validate_behaviors() -> ValidationResponse:
    conforms, report = run_shacl_validation(
        workspace_storage.list_behaviors(),
        workspace_storage.prefixes,
        ontology_service,
    )
    return ValidationResponse(conforms=conforms, report=report)


@app.get("/api/export", response_model=ExportResponse)
def export_behaviors() -> ExportResponse:
    ttl = export_ttl(
        workspace_storage.list_behaviors(),
        workspace_storage.prefixes,
        ontology_service,
    )
    return ExportResponse(ttl=ttl, prefixes=workspace_storage.prefixes)


@app.post("/api/export", response_model=ExportResponse)
def export_behaviors_and_write() -> ExportResponse:
    path = export_to_file(
        workspace_storage.list_behaviors(),
        workspace_storage.prefixes,
        ontology_service,
    )
    ttl = path.read_text(encoding="utf-8")
    return ExportResponse(ttl=ttl, prefixes=workspace_storage.prefixes)


@app.get("/api/export/file")
def export_file():
    path = export_to_file(
        workspace_storage.list_behaviors(),
        workspace_storage.prefixes,
        ontology_service,
    )
    if not path.exists():
        raise HTTPException(status_code=500, detail="Export failed")
    return {"path": str(path)}
