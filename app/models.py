# ============================================================
# app/models.py — Pydantic request/response schemas
#
# These define the shape of JSON that comes IN and goes OUT.
# SQLite returns plain Row objects; we convert them to these.
# ============================================================

from pydantic import BaseModel
from typing import Optional


class Task(BaseModel):
    """What the API sends back to the client."""
    id:    int
    title: str
    done:  bool     # Python bool (converted from SQLite's 0/1)


class TaskCreate(BaseModel):
    """Body the client sends to POST /tasks/"""
    title: str      # required — validated by Pydantic automatically


class TaskUpdate(BaseModel):
    """Body the client sends to PUT /tasks/{id} — both fields optional."""
    title: Optional[str]  = None
    done:  Optional[bool] = None
