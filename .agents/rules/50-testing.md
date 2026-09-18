# Testing and Verification Rules
Required loop:
ANALYZE → PLAN → IMPLEMENT → TEST → BUILD (if applicable) → REGRESSION AUDIT → FIX → VERIFY

If a task-caused check fails: find root cause, fix, rerun failed check and related regression checks.
Maximum 3 repair cycles per failure cluster; then report BLOCKED honestly.

Never weaken tests, hide exceptions, skip failures without explanation, or introduce mock financial data.

DONE requires applicable implementation, tests, build, API/auth/ownership/error checks, regression checks, no task-caused runtime errors, no secret exposure, and no unintended DB changes.
