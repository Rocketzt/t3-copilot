# Team log

**Team-level events only:** gate results, merges to `main`, scope cuts, submission. This is a shared file, so edit
it on `main` only: pull first, make one small commit, push immediately (`ROLES.md`). Ziyu updates it at each gate. Individual work goes in `log/<name>.md`, one file per person, so logs never
conflict on merge. Newest first. The entries below, dated before 2026-10-23 10:30, are project-setup history.

## 2026-10-23 — Roles v2 applied; agent prompts for unattended runs added

**Setup:** Rewrote `ROLES.md` (v2) and updated the folder READMEs to match. Added
`docs/planning/agent_prompts/` with one prompt per member, for AI agents to run unattended on their own branches.
**Result:** Each member has about 9–9.5 h of work. The Excel exports are cut.
**Anomalies:** None.

## 2026-10-23 — Correction: both teammates are already collaborators

**Setup:** Listed the repo's collaborators through the GitHub API.
**Result:** Rocketzt, chrochrohoho and JasonXiao7 are collaborators, with no pending invites. The previous entry's
anomaly ("not yet collaborators, cannot push") was wrong; it was assumed rather than checked.
**Anomalies:** None.

## 2026-10-23 — Roles distributed; per-person branches created

**Setup:** Wrote `ROLES.md`: the owner of every path, the git workflow and the hand-offs. Created the branches
`ziyu`, `jonathan` and `jason` from `main` on GitHub.
**Result:** CONTRACT §0 and EXECUTION_PLAN §2 now map to one owner table (ERRATA C6 resolved). Jason and Jonathan
have pulled the repo; Jason is running the ClawsGO cross-check.
**Anomalies:** Jason and Jonathan are not yet repo collaborators, so they cannot push until invited.

## 2026-10-23 — Logs split into one file per member

**Setup:** Created `log/ziyu.md`, `log/jonathan.md` and `log/jason.md`, each with the same entry format. This file
is limited to team events with a single writer.
**Result:** Each member appends only to their own file, so merges at gates no longer conflict on the log.
**Anomalies:** None.

## 2026-10-23 — EXECUTION_PLAN.md and CONTRACT.md checked: 9 + 9 errata; repo reorganized into the contract layout

**Setup:** Read both new teammate files in full. Rechecked their figures against the workbook with the cell-ref
parser (scratchpad `verify_plan.py`) and a short extra script. The extra script covered:
- the ±0.01 pp rounding rows;
- the peer gaps for the 2024 rows;
- Beiling's size class;
- which packages the repo `.venv` has.
**Result:**
- Their core numbers are correct. That includes the rounding note: exactly 6 of 192 rows differ from (E − H) × 100
  by more than 0.005 pp.
- Errors are listed in `docs/planning/ERRATA.md`:
  - CONTRACT keeps the wrong missing-weather rows;
  - CONTRACT calls Beiling (medium) a small airport;
  - CONTRACT says there is no git requirement;
  - the machine-specific paths, and the owner tables that conflict between the two files;
  - EXECUTION_PLAN wants a private repo and omits the thumbnail and AI statement from the submission;
  - EXECUTION_PLAN quotes test results as achieved before any run.
- The repo `.venv` (Python 3.13.5) has no openpyxl, pandas or Pillow.
- Repo reorganized:
  - added the directories and a README in each;
  - `Track 3 Data.xlsx` moved to the repo root (CONTRACT §3 `DATA_PATH`);
  - records moved to `docs/project/` and the shortlist PDF to `docs/planning/`;
  - PLAN.md removed;
  - added `README.md`, `.env.example`, `requirements.txt`, stubs for deliverables D01 and D03–D07, and
    `docs/AI_USAGE.md`;
  - organizer files moved to the git-ignored `organizer_materials/`.
**Anomalies:** The Track 1 and Track 2 PDFs could not be moved ("Device or resource busy"; open in another program).
They stay in `HackSHSID 2026/`, which is git-ignored.

## 2026-10-23 — Public GitHub repo created and main pushed

**Setup:** Scanned the committed files for keys, tokens, the campus code, the join code, G-numbers, emails and phone
numbers. Then ran `gh repo create Rocketzt/t3-copilot --public --source . --push`.
**Result:** https://github.com/Rocketzt/t3-copilot is PUBLIC with default branch `main`, and the 9 committed files
are visible through the GitHub API. The scan found only the deliberately fake test number in PLAN.md's adversarial
test.
**Anomalies:** None.

## 2026-10-23 — PLAN.md checked against the workbook: numbers correct except the missing-weather rows; local git repo created

**Setup:** A teammate added `PLAN.md` (Track 3 build plan). Recomputed its Appendix A from `Track 3 Data.xlsx` with a
new stdlib parser that reads cells by column letter (scratchpad `verify_plan.py`). Then ran `git init -b main` in
the project root, with `.gitignore` and `.gitattributes`.
**Result:**
- These PLAN.md figures match the workbook exactly:
  - 14 sheets, 192 airport-months;
  - 12 rules (RULE001–012) and 15 tests (TEST001–015);
  - column I = (E − H) × 100, and column G = the same-size mean of column E, both with 0 mismatches;
  - 12 RULE003 flags; signal counts {0: 179, 1: 11, 2: 1, 3: 1};
  - Hailing 2025-07 at −15.62 / −5.46 / −11.48 pp; Yunchuan 2025-07 YoY at −0.80 pp;
  - the network's monthly averages.
- **PLAN.md is wrong about the missing weather rows.** It lists Hailing 2025-03, Gaoyuan 2025-09, Yunchuan 2025-11 and
  Beiling 2025-11. The workbook marks Qinglan 2025-03, Gaoyuan 2025-09, Hailing 2025-11 and Linjiang 2025-11
  (rows 119, 169, 179, 184 of `03_机场天气月度`).
- Minor PLAN.md issues:
  - Appendix A.1 shows the peer gap as "n/a" for 2024 rows, but it can be computed (only YoY is n/a).
  - It refers to a `CONTRACT.md` that is not in the folder.
- Git: the first commit holds the records, PLAN.md, the shortlist PDF and the Track 3 data file. The registration
  guide (it contains the campus code), the zip, the tutorial and the other organizer PDFs are git-ignored. No remote
  has been added.
**Anomalies:** My earlier entries were wrong on four counts, because the first dump script stopped at 12 rows per
sheet and I miscounted the flags. They said 11 rules (actually 12), 11 tests (15), 13 sheets (14) and 11 RULE003 flags
(12). `Track3_Shortlist.pdf` was regenerated with the corrected counts.

## 2026-10-23 — Mini Airways researched as design inspiration for Track 3 (team now leaning to T3)

**Setup:** Two web searches (Steam, App Store, Nintendo listings; GamingOnLinux and a blog review).
**Result:** Mini Airways (CCC Games / Erabit, PC release 2024-07-30) is a minimalist real-time air-traffic-control
game. It has colour-coded aircraft, click-and-drag routing, peak hours that ramp up difficulty, about 19 maps based
on real airports including Beijing Capital and Shanghai Hongqiao, and random historical events. It has no native
weather system that could be confirmed. It is relevant to Track 3 only as UI and demo inspiration; Track 3 asks for
airline decision support, not air-traffic control.
**Anomalies:** The weather mechanics and the depth of the upgrade system could not be verified.

## 2026-10-23 — Track 3 data: RULE003 flags 11 airport-months; Hailing Jul 2025 is the outlier at −15.6 pp

**Setup:** Stdlib Python over `Track 3 Data.xlsx`. Read sheet `01_机场月度运行基线` (192 airport-months), column
"与自身平均差" (gap to own 12-month average, in percentage points), and the "是否缺少数据" (missing data) flag in
`03_机场天气月度`.
**Result:**
- 11 airport-months are more than 5 pp below their own average, which triggers RULE003 (flag for review).
- Hailing (海陵) is −15.62 pp in Jul 2025 and −10.99 pp in Aug 2025, the planted anomaly DQ004. Every other drop
  is between −5.4 and −6.5 pp.
- 4 weather rows are marked missing: Qinglan 2025-03, Gaoyuan 2025-09, Hailing 2025-11, Linjiang 2025-11.
**Anomalies:** None.

## 2026-10-23 — ClawsGO Science is allowed under the AI-tool rule, but cost and onboarding are unknown

**Setup:** Two web searches plus the 36Kr article of 2026-09-23 (the only substantive source found; no official
English site found).
**Result:** ClawsGO Science (北京比特奇迹科技) is a cloud research agent. It runs literature search, code, plots and LaTeX
writing from one prompt, in its own cloud server, for hours. It is publicly open for sign-up. It is paid by usage or
plan; no free tier is mentioned and prices are not published. The hackathon rules allow AI tools if their use is
disclosed and the team checks the output and can explain it.
**Anomalies:** Every detail rests on one news article. Its URL, price and success rate could not be verified.

## 2026-10-23 — Project records set up; track decision pending a team meeting

**Setup:** Created `OVERVIEW.md`, `LOG.md`, `TASKS.md` and `DECISIONS.md` in the project root.
**Result:** The team (3 people) has not chosen a track yet. A meeting is planned to decide.
**Anomalies:** None.

## 2026-10-23 — Reviewed all organizer materials; deadline is 2026-10-24 23:59

**Setup:** Read the 3 track statements, the registration/submission guide and the GitHub tutorial. Parsed every sheet
of `Track 3 Data.xlsx` with a stdlib-only Python script (openpyxl is not installed). Listed the zip contents.
**Result:**
- T1 timetable and T2 data-centre scheduling give no data. T3 gives 13 sheets: 8 fictional airports with monthly
  baselines and weather for 2024–25 (192 rows each), yearly airport sizes, 5 simulated events, 11 operating rules,
  an output template (EVT001 filled as an example), a human-feedback log, 11 test questions and a list of 8 required
  deliverables.
- T3 has deliberate traps: missing weather records (DQ002), a source conflict in EVT003 (DQ003) and a designed drop
  at Hailing airport in Jul–Aug 2025 (DQ004).
- The zip duplicates the folder.
**Anomalies:** None.
