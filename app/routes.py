# ============================================================
# app/routes.py — HTTP endpoints (identical behaviour to A1)
#
# Routes are UNCHANGED from A1 — same paths, same status codes,
# same request/response shapes. Only what's behind them changed.
# This proves the assignment's golden rule:
#   "Only the storage code should be changing."
# ============================================================

from fastapi import APIRouter, HTTPException
from typing import List

from app.models import Task, TaskCreate, TaskUpdate
import app.repository as repo

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ── Stage 1: GET all tasks ────────────────────────────────────

@router.get("/", response_model=List[Task], summary="List all tasks")
def list_tasks():
    """
    SQL behind this: SELECT * FROM tasks ORDER BY id
    Returns all tasks as JSON array.
    """
    return repo.get_all_tasks()


# ── Stage 1: GET one task ─────────────────────────────────────

@router.get("/{task_id}", response_model=Task, summary="Get one task")
def get_task(task_id: int):
    """
    SQL behind this: SELECT * FROM tasks WHERE id = ?
    Returns 404 if task_id doesn't exist — same as A1.
    """
    task = repo.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# ── Stage 2: POST create task ─────────────────────────────────

@router.post("/", response_model=Task, status_code=201, summary="Create a task")
def create_task(body: TaskCreate):
    """
    SQL behind this: INSERT INTO tasks (title, done) VALUES (?, ?)
    Returns 400 if title is missing or blank — same as A1.
    Returns 201 + new task with db-assigned id on success.
    """
    if not body.title or not body.title.strip():
        raise HTTPException(status_code=400, detail="title must not be empty")
    return repo.create_task(body)


# ── Stage 3: PUT update task ──────────────────────────────────

@router.put("/{task_id}", response_model=Task, summary="Update a task")
def update_task(task_id: int, body: TaskUpdate):
    """
    SQL behind this: UPDATE tasks SET title=?, done=? WHERE id=?
    Returns 400 if no fields sent, 404 if not found — same as A1.
    """
    if body.title is None and body.done is None:
        raise HTTPException(status_code=400, detail="send at least one of: title, done")
    if body.title is not None and not body.title.strip():
        raise HTTPException(status_code=400, detail="title must not be empty")

    task = repo.update_task(task_id, body)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# ── Stage 3: DELETE task ──────────────────────────────────────

@router.delete("/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    """
    SQL behind this: DELETE FROM tasks WHERE id = ?
    Returns 204 (no body) on success, 404 if not found — same as A1.
    """
    deleted = repo.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
