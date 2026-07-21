# ============================================================
# app/repository.py — SQLite CRUD queries
#
# All SQL lives here. Routes call these functions; they never
# write SQL themselves. This is the "storage layer" the
# assignment talks about — the only code that changed from A1.
#
# PARAMETERIZED QUERIES — WHY ? EVERYWHERE
# ─────────────────────────────────────────────────────────────
# WRONG (SQL injection risk):
#   cur.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
#   If task_id = "1 OR 1=1", the query returns ALL tasks.
#
# RIGHT (parameterized):
#   cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
#   SQLite escapes the value — user input can never change the query.
#
# Note the trailing comma in (task_id,) — it makes a 1-element tuple.
# Without it, (task_id) is just parentheses around a value, not a tuple,
# and sqlite3 will raise a TypeError.
#
# CONVERTING ROWS TO DICTS
# ─────────────────────────────────────────────────────────────
# sqlite3.Row objects can be accessed by column name (row["id"])
# but Pydantic needs a plain dict or keyword args.
# _row_to_dict() converts Row → dict and maps done (0/1) → bool.
# ============================================================

import sqlite3
from typing import Optional
from app.database import get_connection
from app.models import Task, TaskCreate, TaskUpdate


# ── private helper ────────────────────────────────────────────

def _row_to_task(row: sqlite3.Row) -> Task:
    """
    Convert a SQLite Row to a Pydantic Task.
    Converts done: 0/1 (SQLite integer) → False/True (Python bool).
    """
    return Task(
        id    = row["id"],
        title = row["title"],
        done  = bool(row["done"]),   # 0 → False, 1 → True
    )


# ── Stage 1: Read ─────────────────────────────────────────────

def get_all_tasks() -> list[Task]:
    """
    SQL: SELECT * FROM tasks ORDER BY id
    Returns all rows as a list of Task objects.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY id")
        rows = cur.fetchall()        # list of Row objects
        return [_row_to_task(r) for r in rows]
    finally:
        conn.close()


def get_task_by_id(task_id: int) -> Optional[Task]:
    """
    SQL: SELECT * FROM tasks WHERE id = ?
    Returns one Task or None if not found.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()         # one Row or None
        return _row_to_task(row) if row else None
    finally:
        conn.close()


# ── Stage 2: Create ───────────────────────────────────────────

def create_task(data: TaskCreate) -> Task:
    """
    SQL: INSERT INTO tasks (title, done) VALUES (?, ?)
    SQLite assigns the id automatically (AUTOINCREMENT).
    cur.lastrowid gives us the id that was just assigned.
    Then we fetch the row back to return the complete Task.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (data.title.strip(), 0),   # new tasks always start not done
        )
        conn.commit()                  # write to disk (persists!)
        new_id = cur.lastrowid         # the id SQLite just assigned
        cur.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
        row = cur.fetchone()
        return _row_to_task(row)
    finally:
        conn.close()


# ── Stage 3: Update ───────────────────────────────────────────

def update_task(task_id: int, data: TaskUpdate) -> Optional[Task]:
    """
    SQL: UPDATE tasks SET title = ?, done = ? WHERE id = ?
    Only updates the fields the client actually sent (not None).
    Returns updated Task or None if task_id doesn't exist.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # First check the task exists
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        existing = cur.fetchone()
        if existing is None:
            return None

        # Build update from existing values, only override what was sent
        new_title = data.title.strip() if data.title is not None else existing["title"]
        new_done  = int(data.done)     if data.done  is not None else existing["done"]
        # int(data.done): True → 1, False → 0 (SQLite stores integers)

        cur.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id),
        )
        conn.commit()

        # Return the updated task
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return _row_to_task(cur.fetchone())
    finally:
        conn.close()


# ── Stage 3: Delete ───────────────────────────────────────────

def delete_task(task_id: int) -> bool:
    """
    SQL: DELETE FROM tasks WHERE id = ?
    Returns True if a row was deleted, False if id didn't exist.
    cur.rowcount tells us how many rows the DELETE affected.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cur.rowcount > 0   # 0 = nothing deleted = task didn't exist
    finally:
        conn.close()


# ── Stats (bonus) ─────────────────────────────────────────────

def get_stats() -> dict:
    """
    Uses SQL COUNT(*) instead of counting in Python.
    Two queries: total, and count of done tasks.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
        done = cur.fetchone()[0]
        return {"total": total, "done": done, "open": total - done}
    finally:
        conn.close()
