# HackSHSID 2026 entry — overview (as of 2026-10-23)

This file is the source of truth. If it disagrees with another document, this file wins.

## Goal
Submit a runnable prototype for one HackSHSID 2026 track by **2026-10-24 23:59**, then get shortlisted for the
26–28 Oct presentations (5 min talk + live demo, 3 min Q&A).

## Approach / design
The team is leaning to Track 3 (flight-disruption AI assistant). A teammate's detailed build plan is in `PLAN.md`; its
4-part design matches `Track3_Shortlist.pdf`. Not yet formally decided.

## Status
- Team: 3 people. The track and roles are not yet formally recorded.
- Local git repo created (branch `main`); no GitHub remote yet. No code yet.

## Results so far
None.

## Open questions
- Which track: T1 (school timetable), T2 (data-centre power/compute scheduling) or T3 (flight-disruption AI assistant)?
- Has every member registered on study.standardcas.org and joined one project?

## Settled facts
- The zip `HackSHSID 2026(2)(2).zip` is identical to the `HackSHSID 2026/` folder (same 4 files, same sizes).
- Only Track 3 comes with data (`HackSHSID 2026/Track 3 Data.xlsx`, simulated, in Chinese). T1 and T2 give no data.
- Track 3 workbook facts (verified 2026-10-23, see LOG.md):
  - 14 sheets, 8 airports × 24 months = 192 rows;
  - 12 rules, 15 tests, 5 events, 17 output fields;
  - column I is already percentage points;
  - RULE003 flags 12 airport-months, and only Hailing 2025-07 trips all three comparisons;
  - missing weather rows: Qinglan 2025-03, Gaoyuan 2025-09, Hailing 2025-11, Linjiang 2025-11.
- Teams have at most 3 people, and each person can be on only one project.
- Submission fields: title, short description, track, thumbnail, inspiration/description, public GitHub repo link,
  testing evidence, AI statement.
- Rules: runnable prototype; AI use allowed but must be disclosed and explainable; credit outside code/data;
  no personal info, passwords or API keys in the public repo.
- Timeline: preliminary review 25 Oct; shortlisted presentations 26–28 Oct at lunch.

## Who does what
To be assigned at the track meeting (3 members, names not yet recorded).

## Where things are
- Overview: `OVERVIEW.md` (this file)
- Log: `LOG.md`
- Tasks: `TASKS.md`
- Decisions: `DECISIONS.md`
- Track 3 build plan (teammate's): `PLAN.md`; shortlist: `Track3_Shortlist.pdf`
- Organizer materials: `HackSHSID 2026/`, `Registration & Submission Instructions(5)(2).pdf`, `github_tutorial (1)(1)(2).pdf`
