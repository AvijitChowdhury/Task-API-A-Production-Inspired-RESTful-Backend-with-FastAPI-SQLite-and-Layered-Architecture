# ============================================================
# ai-version/main.py — Stage 6: The AI Rematch
#
# This is the AI-generated version of the same migration.
# It lives in its own folder so the hand-built Stages 0-5
# code stays untouched — that version is the submission.
#
# The prompt used to generate this:
#   See ai-version/PROMPT.md
# ============================================================

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "tasks.db"


# ── Pydantic models ───────────────────────────────────────────

class Task(BaseModel):
    id:    int
    title: str
    done:  bool

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done:  Optional[bool] = None


# ── Database helpers ──────────────────────────────────────────

def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
        """)
        cur.execute("SELECT COUNT(*) FROM tasks")
        if cur.fetchone()[0] == 0:
            cur.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [("Buy groceries", 0), ("Read a book", 1), ("Go for a walk", 0)]
            )
        conn.commit()
    finally:
        conn.close()

def row_to_task(row) -> Task:
    return Task(id=row["id"], title=row["title"], done=bool(row["done"]))


# ── App + lifespan ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Task API — AI Version", lifespan=lifespan)


# ── Endpoints ─────────────────────────────────────────────────

@app.get("/tasks", response_model=List[Task])
def list_tasks():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [row_to_task(r) for r in rows]
    finally:
        conn.close()

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise HTTPException(404, detail=f"Task {task_id} not found")
        return row_to_task(row)
    finally:
        conn.close()

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(body: TaskCreate):
    if not body.title or not body.title.strip():
        raise HTTPException(400, detail="title must not be empty")
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (body.title.strip(), 0)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
        return row_to_task(row)
    finally:
        conn.close()

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, body: TaskUpdate):
    if body.title is None and body.done is None:
        raise HTTPException(400, detail="send at least one of: title, done")
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise HTTPException(404, detail=f"Task {task_id} not found")
        new_title = body.title.strip() if body.title is not None else row["title"]
        new_done  = int(body.done)     if body.done  is not None else row["done"]
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id)
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return row_to_task(row)
    finally:
        conn.close()

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, detail=f"Task {task_id} not found")
    finally:
        conn.close()
