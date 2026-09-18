# Context Efficiency Rules
Goal: minimize unnecessary context/token usage without reducing correctness.

## Progressive disclosure
- Start with project context + core rules.
- Load specialist rules/skills only when the task matches them.
- Search/reference symbols before reading large files.
- Do not reread unchanged files.

## Task routing
Classify each task as DOCS/CONFIG, FRONTEND, BACKEND, SECURITY, DATABASE, AI, or CROSS-CUTTING.
Use the narrowest context that can establish correctness; expand only when dependencies require it.

## Verification budget
- Small/local change: targeted verification.
- Shared API/security/database change: targeted + dependency regression.
- Cross-cutting/high-risk change: broader checks.
Do not run unrelated expensive checks merely for ceremony.

## Context compression
Keep stable facts in canonical project docs. Avoid duplicating the same rules across many files.
Do not paste source files into prompts when the agent can inspect them.
