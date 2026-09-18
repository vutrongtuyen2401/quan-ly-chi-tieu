# Database Rules
SQLite is used.
Before schema changes inspect tables, foreign keys, indexes, reads/writes, migrations, and tests.
Prefer backward-compatible migrations and preserve existing data.
Never reset/drop data as a shortcut.
Financial calculations should be deterministic and appropriately numeric.
