# HackSHSID 2026 entry — overview (as of 2026-10-24 pre-submission)

This file describes the project's current state. For the build plan, `EXECUTION_PLAN.md` wins; for interfaces,
`CONTRACT.md` wins; for numbers, the workbook wins (known plan errors: `docs/planning/ERRATA.md`).

## Goal
Submit a runnable prototype for one HackSHSID 2026 track by **2026-10-24 23:59**, then get shortlisted for the
26–28 Oct presentations (5 min talk + live demo, 3 min Q&A).

## Approach / design
The team is building Track 3 (confirmed 2026-10-23), the flight-disruption AI assistant "T3 Ops Copilot", following `EXECUTION_PLAN.md`. The
assistant has four parts:
1. a detector;
2. a fact sheet → writer → checker;
3. an exam runner;
4. append-only feedback memory.

It is a Python stdlib web app with vanilla JS.

## Status
- **Built and verified.** The full prototype (app, engine, checker, exam runner) is merged on `main`; submission
  text is drafted in `docs/SUBMISSION_DRAFT.md`.
- Public GitHub repo: https://github.com/Rocketzt/t3-copilot (`main`, plus branches `ziyu`, `jonathan` and `jason`).
  Collaborators: Rocketzt, chrochrohoho and JasonXiao7, all able to push.
- D01–D08, `AI_USAGE.md`, `SUBMISSION_DRAFT.md` and the evidence folders are in place. Still open: UI polish,
  fresh screenshots + thumbnail, the submission form and registration checks (see `TASKS.md`).

## Results so far (from real runs; figures in `docs/NUMBERS.md` and the logs)
- Detector: 192 airport-months verified against an independent recomputation and the ClawsGO cross-check
  (0 mismatches; `evidence/ai/clawsgo/`).
- Exam **21/21** — 15 official + 5 own + 1 negative (`python tests/run_tests.py --writer-mode offline`); the
  bad-AI demo is blocked by checker C02.
- Unit tests **56/56 OK**, re-run on 2026-10-24 also from a clean clone of the public repo (fresh venv, pip
  install, exam, app boot, `/` and `/api/health` 200 — `docs/project/log/ziyu.md`, 2026-10-24 22:11 entry).
- Risk labels across the five organizer events: EVT001 Medium, EVT002 Low, EVT003 Can't tell, EVT004 Low,
  EVT005 Low; the network view ranks Hailing first.

## Open questions
- Are all three members registered on study.standardcas.org and joined to one project?
- Is `docs/project/DECISIONS.md` missing an explicit "offline template is the default writer" line? The default
  is applied everywhere (README writer modes, exam runs) and `TASKS.md` records it as decided.

## Settled facts
- The zip `HackSHSID 2026(2)(2).zip` is identical to the organizer folder (same 4 files, same sizes).
- Only Track 3 comes with data (`Track 3 Data.xlsx`, simulated, in Chinese). T1 and T2 give no data.
- Track 3 workbook facts (verified 2026-10-23, see LOG.md):
  - 14 sheets, 8 airports × 24 months = 192 rows;
  - 12 rules, 15 tests, 5 events, 17 output fields;
  - column I is already percentage points; 6 rows differ from (E − H) × 100 by ±0.01 pp because of rounding;
  - RULE003 flags 12 airport-months (11 in July/August), and only Hailing 2025-07 trips all three comparisons;
  - missing weather rows: Qinglan 2025-03, Gaoyuan 2025-09, Hailing 2025-11, Linjiang 2025-11.
- Teams have at most 3 people, and each person can be on only one project.
- Submission fields: title, short description, track, thumbnail, inspiration/description, public GitHub repo link,
  testing evidence, AI statement.
- Rules: runnable prototype; AI use allowed but must be disclosed and explainable; credit outside code/data;
  no personal info, passwords or API keys in the public repo.
- Timeline: preliminary review 25 Oct; shortlisted presentations 26–28 Oct at lunch.
- The repo `.venv` has no openpyxl, pandas or Pillow; install them from `requirements.txt`.

## Who does what
`ROLES.md` holds the single file-owner table and the git workflow. In short:
- **Ziyu** — tech lead: the checker, merges at gates, code review, deliverables D01, D04, D06 and D07;
- **Jonathan** — the web app, the writer and the pipeline; deliverables D02 and D08;
- **Jason** — the data loader, detector, rules, fact sheet, feedback and tests; deliverables D03 and D05; the
  submission form.

## Where things are
- Repo layout: `README.md` (root); roles and file owners: `ROLES.md`
- Build plan: `EXECUTION_PLAN.md`; interface contract: `CONTRACT.md`; errata: `docs/planning/ERRATA.md`
- Records: `docs/project/`:
  - this file;
  - `LOG.md`, team events only (shared; edited on `main`, updated by Ziyu at gates);
  - `log/<name>.md`, one work log per member;
  - `TASKS.md` (shared; edited on `main`, updated by Ziyu at gates);
  - `DECISIONS.md`.
- Deliverable drafts: `docs/D01…D08`; submission text: `docs/SUBMISSION_DRAFT.md`; AI-use log: `docs/AI_USAGE.md`;
  canonical numbers: `docs/NUMBERS.md`; screenshot/demo evidence: `evidence/` (incl. `evidence/runs/`)
- Data: `Track 3 Data.xlsx` (repo root, read-only)
- Organizer materials (local only, git-ignored): `organizer_materials/`. The Track 1 and 2 PDFs are still in
  `HackSHSID 2026/` because they were open in another program.
