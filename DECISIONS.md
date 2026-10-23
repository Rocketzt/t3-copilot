# Decisions

Newest first. A reversal is a new entry.

## 2026-10-23 — Keep project records in four Markdown files at the project root

**Decision:** Use `OVERVIEW.md` (current state, source of truth), `LOG.md`, `TASKS.md` and `DECISIONS.md`.
**Why:** Three people work in parallel against a deadline the next day, so everyone needs one shared place for
the current state.
**Consequence:** Every result, decision or change of plan updates these files in the same step. They can move into
the GitHub repo once it exists. Nothing secret goes in them, because the repo will be public.
