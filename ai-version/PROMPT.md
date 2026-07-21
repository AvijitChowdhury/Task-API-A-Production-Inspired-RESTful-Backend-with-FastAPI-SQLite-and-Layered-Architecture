# Stage 6 — AI Rematch: The Prompt I Used

## My Prompt

```
I have a FastAPI CRUD task API built in Python. It currently stores tasks
in memory (a Python list). I need to migrate its storage to SQLite.

Here is exactly what I need:

**Language and framework:** Python 3.12, FastAPI, sqlite3 (standard library — no ORMs).

**Database file:** tasks.db — created automatically in the project root if it doesn't exist.

**Table schema:**
  - Table name: tasks
  - Columns: id (INTEGER PRIMARY KEY AUTOINCREMENT), title (TEXT NOT NULL), done (INTEGER NOT NULL DEFAULT 0)
  - done stores 0 for false and 1 for true — SQLite has no boolean type.

**Startup behaviour:**
  - Create the table if it doesn't already exist (CREATE TABLE IF NOT EXISTS).
  - Seed exactly three example tasks ONLY if the table is empty (COUNT(*) = 0 check first).
  - Seeds: ("Buy groceries", 0), ("Read a book", 1), ("Go for a walk", 0)
  - Restarting must NOT duplicate seeds.

**Five endpoints — identical behaviour to the in-memory version:**
  - GET  /tasks          → 200, list all tasks
  - GET  /tasks/{id}     → 200 task | 404 {"detail": "Task {id} not found"}
  - POST /tasks          → 201 new task | 400 if title missing or blank
  - PUT  /tasks/{id}     → 200 updated | 400 if no fields sent | 404 if not found
  - DELETE /tasks/{id}   → 204 no body | 404 if not found

**Pydantic schemas:** Task(id, title, done), TaskCreate(title), TaskUpdate(title?, done?)

**Safety:** ALL queries must use parameterized placeholders (?). No user input
concatenated into SQL strings.

**Parameterized query rule for tuples:** always use (value,) not (value)
for single-value parameters — the trailing comma makes it a tuple.

Please put everything in a single main.py file.
```
