# ============================================================
# main.py — Application entrypoint
#
# What changes from A1:
#   • lifespan calls init_db() on startup — creates tasks.db
#     and seeds 3 example tasks if the table is empty
#   • Everything else (routes, port, docs URL) is identical
# ============================================================

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.routes import router as tasks_router
from app.database import init_db
import app.repository as repo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once on startup before accepting requests.
    init_db() creates tasks.db + table + seeds if first run.
    """
    init_db()   # Stage 0: create DB, table, seed
    yield       # server is now running


app = FastAPI(
    title="Task API — W3 A2",
    description=(
        "CRUD API for tasks — FastAPI + SQLite.\n\n"
        "Storage: `tasks.db` (created automatically on first run).\n\n"
        "Data **survives server restarts** — that's the whole point of Week 3."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.include_router(tasks_router)


@app.get("/", tags=["info"], summary="API info")
def root():
    return {
        "name":    "Task API",
        "version": "2.0.0 — W3 A2",
        "storage": "SQLite (tasks.db)",
        "docs":    "/docs",
    }


@app.get("/health", tags=["info"], summary="Health check")
def health():
    return {"status": "ok"}


@app.get("/stats", tags=["info"], summary="Task statistics (SQL COUNT)")
def stats():
    """
    Stretch goal: statistics computed with SQL COUNT(*) — not Python loops.
    SELECT COUNT(*) FROM tasks
    SELECT COUNT(*) FROM tasks WHERE done = 1
    """
    return repo.get_stats()


# ── Run locally ───────────────────────────────────────────────
# python -m uvicorn main:app --reload
# Open: http://localhost:8000/docs
