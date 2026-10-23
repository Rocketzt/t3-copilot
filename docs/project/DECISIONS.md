# Decisions

Newest first. A reversal is a new entry.

## 2026-10-23 — Track 3 confirmed; roles fixed in ROLES.md; shared records edited on main only

**Decision:**
- The team builds Track 3.
- Ziyu: engine and AI core. Jonathan: product and integration (integration captain). Jason: evidence and delivery.
- `ROLES.md` is the single file-owner table and replaces CONTRACT §0.
- Each person works on their own branch.
- Shared records are edited on `main` only (pull, one small commit, push). This replaces the earlier
  "only Jonathan writes LOG/TASKS" rule; Jonathan still updates them at each gate.
**Why:**
- CONTRACT §0 (5 roles) and EXECUTION_PLAN §2 (3 named people) disagreed, which would cause file clashes.
- Small, immediate commits on `main` avoid conflicts without making one person a bottleneck.
**Consequence:**
- `engine/exports.py` and `/api/export/sheet06` are dropped; the exports live in `scripts/build_excel_exports.py`.
- `docs/AI_USAGE.md` is compiled by Jason from **AI:** log entries.

## 2026-10-23 — One work log per member; shared records get a single writer; no conda

**Decision:**
- Each member logs in `docs/project/log/<name>.md`.
- `LOG.md` (team events) and `TASKS.md` are written only by Jonathan, the integration captain, at gates.
- Environments: `.venv` + `requirements.txt`; no conda environment file.
**Why:**
- With three branches inserting entries at the top of one file, every gate merge would conflict.
- The app needs only the standard library, and the build scripts need three pip packages. A conda file would be a
  second environment definition to keep in sync.
**Consequence:** Merges at gates touch disjoint log files. Conda users can still create a Python 3.10+ env and run
`pip install -r requirements.txt`.

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
