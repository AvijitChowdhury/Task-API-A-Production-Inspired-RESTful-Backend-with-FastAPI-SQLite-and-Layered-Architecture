# ============================================================
# app/database.py — SQLite setup
#
# SQLite ships with Python — no pip install needed.
# The database lives in a single file: tasks.db
# It is created automatically the first time the app runs.
#
# KEY CONCEPTS
# ─────────────────────────────────────────────────────────────
# sqlite3.connect("tasks.db")
#   Opens the file. If it doesn't exist, SQLite creates it.
#   That's your entire "database server" — one file.
#
# cursor
#   A cursor is your "pen" for writing SQL commands.
#   You create one from the connection and use it to execute
#   queries: cursor.execute("SELECT * FROM tasks")
#
# connection.commit()
#   Writes pending changes to disk. Without this, INSERTs and
#   UPDATEs are buffered in memory and lost on crash.
#   SELECT queries don't need a commit.
#
# Parameterized queries: cursor.execute("... WHERE id = ?", (id,))
#   The ? is a placeholder. You NEVER put user input into the
#   SQL string directly — that causes SQL injection attacks.
#   SQLite escapes the value safely for you.
#
# row_factory = sqlite3.Row
#   Makes rows behave like dicts: row["id"] instead of row[0].
#   Makes the code much more readable.
# ============================================================

import sqlite3
from pathlib import Path

# tasks.db sits in the project root (next to main.py)
DB_PATH = Path(__file__).parent.parent / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """
    Open and return a SQLite connection.

    row_factory = sqlite3.Row lets us access columns by name:
      row["title"]  ✓
      row[1]        ✗ (fragile — breaks if column order changes)

    Called once per request (same pattern as SQLAlchemy's get_db).
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row   # access columns by name
    return conn


def init_db() -> None:
    """
    Called once at application startup (in main.py lifespan).

    Stage 0 — What this does:
      1. CREATE TABLE IF NOT EXISTS tasks
         Creates the tasks table only if it doesn't already exist.
         Safe to call every startup — never duplicates the table.

      2. Seed three example tasks — BUT only when the table is empty.
         We COUNT(*) first; if 0 rows exist, we insert the seeds.
         This stops the seed from multiplying on every restart.

    SQLite column types used:
      INTEGER PRIMARY KEY  → auto-incrementing id (SQLite handles this)
      TEXT NOT NULL        → the task title
      INTEGER NOT NULL     → done: 0 = false, 1 = true (SQLite has no BOOL)
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        # ── Step 1: Create table ──────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
        """)
        # Note: AUTOINCREMENT means SQLite assigns the next id automatically.
        # We never pass an id on INSERT — the DB fills it in.

        # ── Step 2: Seed only when empty ──────────────────────
        cur.execute("SELECT COUNT(*) FROM tasks")
        count = cur.fetchone()[0]

        if count == 0:
            # Table is empty (first run) — insert seed data
            # This is a transaction: all three inserts succeed or none do.
            cur.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Buy groceries", 0),
                    ("Read a book",   1),
                    ("Go for a walk", 0),
                ]
            )
            conn.commit()   # write to disk
            print("Database seeded with 3 example tasks.")
        else:
            print(f"Database already has {count} tasks — skipping seed.")

    finally:
        conn.close()   # always close — releases the file lock
