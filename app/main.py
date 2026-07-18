from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.models import RunReceipt, RunRequest
from app.service import run_objective
from app.store import get_receipt, initialize, list_receipts

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize()
    yield


app = FastAPI(
    title="BoundedRun",
    version="0.1.0",
    description="Governed AI execution for bounded Codex workflows.",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "boundedrun"}


@app.post("/api/runs", response_model=RunReceipt)
def create_run(request: RunRequest) -> RunReceipt:
    return run_objective(request)


@app.get("/api/runs", response_model=list[RunReceipt])
def recent_runs(limit: int = Query(default=20, ge=1, le=100)) -> list[RunReceipt]:
    return list_receipts(limit)


@app.get("/api/runs/{run_id}", response_model=RunReceipt)
def read_run(run_id: str) -> RunReceipt:
    receipt = get_receipt(run_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Run not found")
    return receipt
