# Backend Rules
Stack: FastAPI + SQLite/Python.
Inspect route, dependencies, models, usages, and tests before editing.
Preserve API paths/methods/response shapes unless explicitly changed.
Preserve data and foreign-key integrity. Use existing migration conventions for schema changes.
Do not do large unrelated `main.py` refactors.
Backend validation is authoritative; do not rely solely on frontend validation.
