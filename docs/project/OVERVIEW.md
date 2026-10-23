# HackSHSID 2026 entry — overview (as of 2026-10-23)

This file describes the project's current state. For the build plan, `EXECUTION_PLAN.md` wins; for interfaces,
`CONTRACT.md` wins; for numbers, the workbook wins (known plan errors: `docs/planning/ERRATA.md`).

## Goal
Submit a runnable prototype for one HackSHSID 2026 track by **2026-10-24 23:59**, then get shortlisted for the
26–28 Oct presentations (5 min talk + live demo, 3 min Q&A).

## Approach / design
The team is building Track 3, the flight-disruption AI assistant "T3 Ops Copilot", following `EXECUTION_PLAN.md`. The
assistant has four parts:
1. a detector;
2. a fact sheet → writer → checker;
3. an exam runner;
4. append-only feedback memory.

It is a Python stdlib web app with vanilla JS.

## Status
- Planning documents and the repo skeleton (directories plus a README in each) are in place. No code yet.
- Public GitHub repo: https://github.com/Rocketzt/t3-copilot (branch `main`). Teammates not yet invited.

## Results so far
- `EXECUTION_PLAN.md` and `CONTRACT.md` were checked against the workbook. Their numbers are correct except for the
  items in `docs/planning/ERRATA.md` (LOG.md 2026-10-23).

## Open questions
- Is the offline template the default writer? Both plans say yes; the earlier shortlist had dropped "backup mode".
- One file-owner table: CONTRACT §0 and EXECUTION_PLAN §2 disagree.
- Has every member registered on study.standardcas.org and joined one project?

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
Per `EXECUTION_PLAN.md` §2:
- **Ziyu** — engine and AI core;
- **Jonathan** — product and integration;
- **Jason** — evidence and delivery.

## Where things are
- Repo layout: `README.md` (root)
- Build plan: `EXECUTION_PLAN.md`; interface contract: `CONTRACT.md`; errata: `docs/planning/ERRATA.md`
- Records: `docs/project/`:
  - this file;
  - `LOG.md`, team events only, written by Jonathan;
  - `log/<name>.md`, one work log per member;
  - `TASKS.md`, written by Jonathan at gates;
  - `DECISIONS.md`.
- Deliverable drafts: `docs/D01…D07`; AI-use log: `docs/AI_USAGE.md`
- Data: `Track 3 Data.xlsx` (repo root, read-only)
- Organizer materials (local only, git-ignored): `organizer_materials/`. The Track 1 and 2 PDFs are still in
  `HackSHSID 2026/` because they were open in another program.
