# Security and Data Integrity Rules
Authentication identifies the user; authorization determines what they may access.
Every user-owned resource ID must be checked against the authenticated user's ownership before read/update/delete/use.
Audit at minimum wallet, category, transaction, budget, recurring transaction, debt, saving goal, and transfers.
Do not trust stale JWT active/role state when current DB state matters.
Never leak another user's data.
OCR/AI failure must never become fabricated financial success.
Never expose secrets.
