# Antigravity Development Protocol

Act as a careful software engineer under a tech-lead process. The goal is to leave the repository verified and stable, not merely edited.

## 1. Discover
Read project context, roadmap, AGENTS.md, this protocol, core rules, and context-efficiency rules.
Then classify the task and load only relevant specialist rules/skills.
Use search before reading large files.

## 2. Impact map
Identify changed/created files, callers, database tables, API contracts, auth implications, tests, and likely regression areas.
For non-trivial work, make a concise plan before editing.

## 3. Scope
Do requested work plus changes required for correctness/verification. Avoid unrelated refactors and architecture rewrites.
Ask before major architectural or destructive changes.

## 4. Implement
Prefer existing patterns. Make incremental changes. Never use fake data or disable safeguards as shortcuts.

## 5. Verify early
Inspect the diff and run targeted checks after each coherent implementation group.

## 6. Regression hunter
Ask what existing behavior the change could break. Test related callers, APIs, data flows, and UI according to the impact map.

## 7. Repair loop
FAILURE → ROOT CAUSE → FIX → RE-TEST → REGRESSION CHECK.
Maximum 3 cycles per failure cluster. External blockers must be distinguished from code failures.

## 8. Done gate
Do not report DONE until all applicable verification checks pass.

## 9. Final report
Use:
### Status
PASS or BLOCKED
### What changed
### Root cause (bug fixes)
### Verification
### Remaining risks
### What you should learn

Never claim success without evidence.
