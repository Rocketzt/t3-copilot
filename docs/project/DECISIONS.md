# Decisions

Newest first. A reversal is a new entry.

## 2026-10-23 — Repo layout follows CONTRACT.md; records move to docs/project/; PLAN.md removed

**Decision:**
- Use the folder layout from CONTRACT.md and EXECUTION_PLAN Appendix E: `app/`, `engine/`, `scripts/`, `tests/`,
  `data/`, `fixtures/`, `exports/`, `evidence/`, `docs/`.
- Keep `Track 3 Data.xlsx` at the repo root, where CONTRACT §3's `DATA_PATH` expects it.
- Move the project records to `docs/project/`.
- Remove `PLAN.md` from the repo; it is still in git history (commit 65cc926).
- Keep organizer materials local only, in `organizer_materials/`.
**Why:**
- The contract is the frozen interface the three builders code against, so the layout matches it rather than the
  other way round.
- EXECUTION_PLAN Appendix D marks PLAN.md as the superseded draft, and it carries the wrong missing-weather list.
**Consequence:** Teammates' files (`EXECUTION_PLAN.md`, `CONTRACT.md`) were not edited; their errors are listed in
`docs/planning/ERRATA.md` for the authors to fix.

## 2026-10-23 — Keep project records in four Markdown files (now in docs/project/)

**Decision:** Use `OVERVIEW.md` (current state, source of truth), `LOG.md`, `TASKS.md` and `DECISIONS.md`.
**Why:** Three people work in parallel against a deadline the next day, so everyone needs one shared place for
the current state.
**Consequence:** Every result, decision or change of plan updates these files in the same step. They can move into
the GitHub repo once it exists. Nothing secret goes in them, because the repo will be public.
