# Errata for EXECUTION_PLAN.md and CONTRACT.md

**Items not ticked here are historical; the build followed ROLES.md and the reviewed code on main.**

Checked 2026-10-23 against `Track 3 Data.xlsx` with an independent stdlib script, which reads cells by column letter.
Each owner fixes their own file; tick an item off when it is fixed. Where a plan and the workbook disagree, the
workbook wins.

**Verified correct in both:**
- 192 airport-months, 12 rules, 15 tests;
- column I = (E − H) × 100, and column G = the same-size mean of E;
- 12 RULE003 flags (11 in July/August), signal counts {0: 179, 1: 11, 2: 1, 3: 1};
- the Hailing and Yunchuan figures, the network monthly averages;
- the "6 rows differ by ±0.01 pp" rounding note.

## CONTRACT.md

| # | Where | Error | Fix |
|---|---|---|---|
| C1 | §2, missing-weather rows | Lists 海陵 2025-03, 高原 2025-09, 云川 2025-11, 北岭 2025-11 | **青岚 Qinglan 2025-03, 高原 Gaoyuan 2025-09, 海陵 Hailing 2025-11, 临江 Linjiang 2025-11** (sheet 03 rows 119, 169, 179, 184). The §4 validation also uses this list |
| C2 | §2, YoY flags | "one small airport 2025-12" | It is **北岭 Beiling, a medium airport**: YoY −5.59 pp |
| C3 | §0 | "Do not commit or add git hooks; there is no git repo requirement" | Wrong. The submission **requires a public GitHub repo**, and the commit history is what reviewers see. Repo: https://github.com/Rocketzt/t3-copilot |
| C4 | Header | Workspace root `D:\下载\HackSHSID 2026` and the Python path `C:\Users\jonat\...` are one person's machine | Use the repo root; the Python 3.10+ stdlib at runtime; `requirements.txt` for build scripts |
| C5 | Header | Says the Python install "has openpyxl, pandas, Pillow" | True only on that machine; the repo `.venv` has none of them. Run `pip install -r requirements.txt` |
| C6 | §0 vs EXECUTION_PLAN §2 | File owners disagree. CONTRACT has 5 roles (Lead, A–D) for 3 people: e.g. `app/server.py` → Lead, `tests/*` → C. EXECUTION_PLAN gives `server.py` to Jonathan and `tests/runner.py` to Ziyu | **Resolved 2026-10-23:** `ROLES.md` is the single owner table |
| C7 | §5, RULE003 | Fires on `signal_count >= 1`, so Beiling 2025-12 fires on YoY alone (own −4.74 pp) | The organizer rule is own-history only (> 5 pp below its own average). Fire on `signals.own`, or document the deviation in D04 |
| C8 | §5, RULE007 | Also fires on "risk level Medium+" | The organizer trigger is only the decision keywords (cancel / release / dispatch / maintenance / compensation). Listing the human decisions every time is fine, but say so in D04 |
| C9 | §4, `airport_context` | When an event has no date, picks the latest 2025 month with ≥ 2 signals, so EVT001 "Day 4" is shown against Hailing **2025-08** | This is an assumption, not a fact. The output should label the month as "latest anomalous month used as context" |

## EXECUTION_PLAN.md

| # | Where | Error | Fix |
|---|---|---|---|
| E1 | Header, Appendix D | Working folder `D:\下载\HackSHSID 2026`; lists `research/`, `build/`, `engine/`, `scratch/`, `.tmp/` and OPSDESK/MiniAirways files that are not in this repo | Refer to the repo layout in `README.md` |
| E2 | Header | Deadline is "assumed" | Confirmed by the registration page: **Sat 24 Oct 2026, 11:59 PM** |
| E3 | §12.1 step 3 | "GitHub private or shared folder" | It must be **public**, and it already exists (see C3) |
| E4 | §12.2 | The submission is described as a folder of zips | The real submission is the study.standardcas.org form: title, short description, track, **thumbnail image**, inspiration/description, public GitHub link, testing evidence, **AI statement**. Add the thumbnail and the AI statement (from `docs/AI_USAGE.md`) to the checklist |
| E5 | Appendix A.1 | Peer gap shown as "n/a" for the 2024 rows | It can be computed. Linjiang 2024-07 −1.26, Qinglan 2024-07 +0.26, Qinglan 2024-08 −1.60, Yunchuan 2024-07 +0.12 pp. Only YoY is n/a. Signals are unchanged |
| E6 | §9.1, §9.2 | The demo script and Q&A state "15/15 + 5/5" and "fabrications blocked" as results | These are targets until the runner produces them; §8.4 of the same plan says so. Quote the real run |
| E7 | §5.2 J1 | Done-when reads "`运行` shows 模拟 badge" (stray word) | "the page shows the 模拟 badge" |
| E8 | §2.1 | "Jonathan (you)" and "your strength" — written to one reader | Use names only in a shared plan |
| E9 | — | ~~Work starts at 22:50 tonight~~ | **Withdrawn 2026-10-24:** not an error. The reviewer's PC clock was UTC−5; 22:50 China time was correct |

## Open decision for the team

**Offline template as the default writer.** Both plans make it the default, which protects the live demo. The
earlier shortlist had dropped "backup mode". Pick one and record it in `docs/project/DECISIONS.md`.
