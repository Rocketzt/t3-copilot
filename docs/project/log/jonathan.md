# Work log — Jonathan (product and integration)

Only Jonathan edits this file, so it never conflicts on merge. Newest entry first, written the same day as the work.
Team-level events (gates, merges, submission) go in `../LOG.md`.

Entry format (copy for each new entry):

```markdown
## YYYY-MM-DD HH:MM — <what was found or finished, not just what was done>

**Setup:** what you did, which files/commit, inputs and settings, how you checked it.
**Result:** the outcome, with numbers and how many cases; what changed because of it.
**Anomalies:** anything surprising, failed or skipped ("None." if none).
**AI:** (only if an AI tool helped) tool, what it did, what you kept or changed.
```

---

## 2026-10-24 17:05 — Network priority map added; `/api/network` self-tested with a real browser

**Setup:** First committed the pending working-tree polish (`b4ba664`: README, UI tag/health polish, evidence
screenshots and D08/reproducibility docs) as instructed. Then fetched, switched to `jonathan` and pulled
(already up to date). `engine/network.py` is **not on this branch**, so I generated
`fixtures/mock_network.json` from the local engine with the same shape as Jason's `network_view` (8 airports,
`priority_rank`, month, signals, verdict, confidence, own/peer/YoY gaps, weather status, reason; plus all 24
months under `by_month` for optional `?year=&month=`); the fixture is clearly labelled `mode: "mock"` and the
server uses `engine.network.network_view` automatically as soon as that module is present. Added
`GET /api/network` (year+month or neither; 400 on a partial pair), a schematic SVG map on the Detector tab
(8 circles, colour by verdict, radius by importance, hover reason, keyboard/click drill-down into the Assistant
tab, `schematic — not geographic` caption, persistent `模拟` labels), a ranked priority table below it, and the
airline-voice wording in README and the About tab.
**Result:** `/api/network` returns 200 with `month_mode=context`, `mode=mock`, 8 airports, `sim_label` and ranks
1–8; `?year=2025&month=7` returns `month_mode=fixed`, Hailing 3 signals / clearly unusual / rank 1; a partial
query returns 400; `/api/analyze` EVT001 still returns `engine_mode=real`, risk `Medium`. Headless Chrome (CDP)
opened `?tab=detector`: **8 network nodes, 8 table rows**, mode label `mock fixture · month: context · 模拟`, and
clicking Hailing switched to the Assistant tab with the result visible, **17 fields**, risk `Medium` and status
`Analyzed EVT001 ... engine mode: real` — **0 console errors**. Screenshot captured at
`%TEMP%\t3_detector.png` (map + legend + ranked table render correctly). `node --check app/static/app.js` passes.
**Anomalies:** `engine.network` exists on `origin/jason` and `origin/main` but is not merged into this branch;
the mock mode is explicit and will switch to real automatically after the merge. `data/feedback.jsonl` is a
runtime log and stays untracked. The old server on 8803 was stopped after the test.
**AI:** DeepSeek Harness — committed the pending handover, generated the fixture, implemented `/api/network`, the
SVG map/legend/table and the airline wording, ran the CDP browser test and wrote this entry.

## 2026-10-24 16:30 — Repo updated; self-check found 13 small issues; plain-language plan written

**Setup:** Fetched every remote branch and merged `origin/main` (`396598b`) into `jonathan` — clean, one docs file
changed. Ran the full self-check: `python -m unittest discover -s tests` (16 tests), `python tests/run_tests.py
--writer-mode offline`, a stdlib `urllib` suite against `app/server.py` (15 endpoints), detector values against
`EXECUTION_PLAN` Appendix A, `scripts/build_data.py` reproducibility, `node --check app.js`, and a read-only
compatibility probe of Ziyu's checker from `origin/ziyu` (extracted to a temp file, **not merged**). Wrote
`docs/planning/UPDATE_PLAN_2026-10-24.md` in plain language.
**Result:** `main` has Jason's engine but **not** Ziyu's checker (`origin/ziyu` `ed1b336` has `engine/checker.py`).
Unit tests **16/16 OK**; HTTP **15/15**; detector canonical values exact; `data/track3.json` rebuilds identically.
Exam **0/21**, but **20/21 cases satisfy every must/must-not pattern** and fail only `pipeline checker did not
pass`; NEG001 fails `bad writer was not blocked` — both are checker-dependent. Checker probe: EVT001–EVT005 pass
after two writer changes (drop derived reason lines from f05; use the exact phrase "official channels"); custom
IDs still fail C02. Plain-language bugs/plans B1–B13 include: missing checker (P0), f05 extra numbers (P0),
passenger phrase (P0), custom IDs (P0), UI "Can't tell" shown as Medium and purple style lost (P1), detector
tab/event cards still read fixtures while analysis uses the real engine (P1), mixed Chinese/English feedback
seeds (P1), typed events with no ID (P1), `tests/run` missing `available`, phrase-scrub grammar, offline
build-package note, stale docs.
**Anomalies:** No code fixes were made in this pass — this is the plan. No `jason`/`ziyu` branch was merged; the
checker was only evaluated read-only. `exports/test_results.json` was refreshed by the self-check.
**AI:** DeepSeek Harness — updated the repo, ran the checks, probed the checker and wrote the plan.

## 2026-10-24 14:05 — Merged main; pipeline uses Jason's real engine; exam 0/21 (checker-only failures)

**Setup:** Ran `git merge origin/main` (main now `28aaea4`); it brought `engine/data.py`, `detector.py`, `rules.py`,
`facts.py`, `feedback.py`, `data/track3.json` and `tests/*`. Then changed only my files:
`engine/pipeline.py` now calls `facts.build_factsheet(event_or_custom, data, year, month)` whenever Jason's modules
import and returns `engine_mode = "real"` (fixtures only if the import fails); custom events pass their own
date/month; `ask()` accepts the CONTRACT `event=` keyword (id string or custom dict); `engine/writer.py` risk labels
are exactly `Low` / `Medium` / `High` / `Can't tell` and it never emits `weather caused` / `caused by weather` (the
pipeline also scrubs echoed event text); `engine/qa.py` answers were aligned with the official must/must-not patterns.
**Result:** EVT001/EVT003/EVT005 run in **real** mode with risk `Medium` / `Can't tell` / `Low`; the hostile OWN005
input comes back with `张伟`/`13812345678` absent and no causal phrase; `ask(event=...)` works for both strings and
dicts. `python tests/run_tests.py --writer-mode offline` → **0/21 passed**, but **20/21 cases satisfy every
must/must-not pattern** and fail only with `pipeline checker did not pass` (TEST001–015 and OWN001–005). The
remaining case, NEG001, fails `bad writer was not blocked`. Both are checker-dependent: `engine/checker.py` (Ziyu)
is not on this branch, so no fake pass was introduced. `python -m unittest tests.test_detector tests.test_facts`
passes **13/13**.
**Anomalies:** The exam cannot report a real pass until Ziyu's checker is merged; the failure list is exactly the
expected checker-dependent set. `main` had advanced and is now merged into this branch.
**AI:** DeepSeek Harness — merged, rewired the pipeline/writer/QA, ran the exam and wrote this entry.

## 2026-10-24 13:40 — PUSH COMPLETED: `jonathan` is on GitHub at `466f2d6`

**Setup:** HTTPS to `github.com:443` was blocked, so I used SSH (port 22 was reachable) with a dedicated key
(`~/.ssh/t3_copilot_ed25519`), added to the `chrochrohoho` GitHub account. The first SSH push was rejected by GitHub
with **GH007** ("push would publish a private email address") because the six build commits used the private
`jonathan_lee2018@outlook.com`. I rewrote only those six commits (range `8191d3d..HEAD`) to the GitHub noreply
identity **`155823325+chrochrohoho@users.noreply.github.com`**; `origin` was switched to
`git@github.com:Rocketzt/t3-copilot.git` with a repo-local `core.sshCommand` pointing at the key.
**Result:** `git push origin jonathan` succeeded as a fast-forward: `d2b2700..466f2d6`; SSH `ls-remote` and the
GitHub API both show `refs/heads/jonathan` = **`466f2d6`**. The branch has 6 commits on top of `main@f70aecf`.
`git fetch` over SSH also refreshed origin: `main` is now **`28aaea4`**, `jason` **`74fd394`**, `ziyu` `d2b2700`.
**Anomalies:** No force push and no push to `main`. The rewrite changed the six commit hashes; a local safety branch
`backup-jonathan-pre-push` = `76fd69b` is kept (not pushed). The branch is based on the older `main@f70aecf`; it has
not been merged with the newer `origin/main@28aaea4` (not requested). The SSH key can be removed from GitHub after
the event.
**AI:** DeepSeek Harness — retried the push, diagnosed auth/email blocks, rewrote the author emails, pushed and wrote
this entry.

## 2026-10-24 00:58 — FINISH: unattended build complete; 15/15 endpoint self-test passed

**Setup:** Built Phases 1–3 unattended on branch `jonathan` from `main` at `f70aecf`. Inputs:
`Track 3 Data.xlsx` (read-only), `CONTRACT.md` §6/§8, `EXECUTION_PLAN.md` §3/§9, `docs/planning/ERRATA.md`.
Fixtures were generated from the workbook with the machine's bundled `openpyxl` (build-time only); the app runs on
the Python 3.12.10 standard library. Started `python app/server.py` on **port 8803**, called every endpoint once
with a stdlib `urllib` script, then stopped the server (port confirmed free afterwards) and removed the test
feedback record.
**Result:** **15/15** endpoint calls returned the expected status and valid JSON:
health · bootstrap (8 airports / 192 airport-months / 12 rules / 15 tests) · detector ranking (192 rows, 12 official
flags, 13 any-signal) · detector chart (24 months, 2 series) · detector airport (Hailing → 2025-08, unusual, 2
signals) · feedback GET (3 seeds) · static index · sheet06 correctly 404 (cut) · analyze EVT001 (17 fields, risk
Medium) · analyze custom (Linjiang, risk Medium) · analyze bad (contains the fabricated "20 points") · ask
(delay-certainty answer) · feedback POST (append works) · tests run (clear "runner not available" message) ·
checker demo (clear "checker not available" message). `node --check app/static/app.js` passes. All pages carry
`模拟 / SIMULATED`.
**What is real vs fixture:** real — writer, pipeline, server, UI, feedback log, detector ranking/chart data generated
from the organizer workbook. Fixture-backed — `engine.data/detector/rules/facts/feedback` are not on this branch, so
`engine/pipeline.py` reads `fixtures/mock_*.json` and reports `engine_mode = "fixture"`. Not available — Ziyu's
`engine/checker.py` (the UI shows "not checked", never a fake pass) and Jason's exam runner (exam tab shows the
message).
**How to start it (morning):** `run_app.bat` (or `python app/server.py`) → open `http://127.0.0.1:8803`.
**Requests for teammates:**
- **Ziyu:** add `engine/checker.py` with `check_output(output, facts) -> {"passed": bool, "checks": [...], "failures": [...]}`;
  the pipeline imports it automatically and the checker panel/demo will light up.
- **Jason:** add `engine/data.py`, `detector.py`, `rules.py`, `facts.py`, `feedback.py` and `tests/runner.py`
  (`run_all(writer_mode=...)`); the pipeline imports them in `try/except` and switches `engine_mode` when present.
  The fixtures are only the fallback, not the answer.
**Anomalies:** `pip install -r requirements.txt` could not reach PyPI (cancelled after ~20 min); the runtime does not
need it. `git fetch`/`ls-remote` to github.com failed with connection reset; **`git push origin jonathan` also failed
twice** (connection reset, then "Couldn't connect to server" on port 443), so the five commits of this build are
**local only** and the remote `origin/jonathan` still points at `d2b2700`. `https://api.github.com` is reachable and
reads the repo, but there is no `gh` CLI and no stored GitHub credential, so an authenticated API commit/push is not
possible from this session. The two untracked planning notes (`R1-R3_*.md`) were moved out of the repo so the working
tree is clean. The local branch was `Jonathan`; `git switch jonathan` resolved it and the merge with `origin/main`
was already up to date.
**AI:** DeepSeek Harness — executed setup, generated fixtures, wrote the writer/pipeline/QA/server/UI, ran the
self-test and this log.

## 2026-10-24 00:52 — Phase 3: five-tab offline UI

**Setup:** Wrote `app/static/index.html`, `app.js`, `styles.css` (vanilla JS, no CDN, no build step): header with the
persistent `模拟 / SIMULATED` badge; tabs Assistant (default), Detector, Exam, Feedback, About. Assistant has the five
event cards, the new-event form, writer mode (Offline / Demo bad AI), risk + detector cards, fact sheet with
assumptions/unknowns/missing data, the 17-field grid with a tag parser, three message tabs with Copy, the checker
panel, the Accept/Edit/Reject bar posting to `/api/feedback`, prior-feedback panel, and the bounded question chips.
Detector has five stat cards, a 192-row ranking table with filter/verdict select, and an inline-SVG Hailing vs
Yunchuan chart with the dashed peer line and 2025-07/08 highlight. Exam, Feedback and About render from the API.
`node --check app/static/app.js` passes.
**Result:** All five tabs work against the real endpoints; no external assets are requested. Empty/error/loading
states are handled, and the checker panel shows "not checked" while Ziyu's checker is absent.
**Anomalies:** No browser automation is available in this run; the UI was validated by the JS syntax check, static
server check and the endpoint responses it consumes.
**AI:** DeepSeek Harness — wrote the UI and checked it.

## 2026-10-24 00:50 — Phase 2: pipeline, bounded QA and stdlib server

**Setup:** Wrote `engine/pipeline.py` (`analyze`, `ask`, `bootstrap`, `detector_ranking`, `chart`,
`detector_airport`, feedback read/append, `run_bad_writer_demo`, `run_tests`, `health`) with
`try/except` imports of Jason's and Ziyu's modules and a fixture fallback. When `engine/checker.py` is missing,
`check = {"passed": null, "detail": "checker not available ..."}` — never a fake pass. Wrote `engine/qa.py`
(bounded bilingual intent router: delay certainty, why-risk, conflict, causality, auto action, PII, simulation,
send, rejection, downgrade, time range, stop, two messages, new airport, fallback) and `app/server.py`
(stdlib `ThreadingHTTPServer`, port `T3_PORT` default 8803, static files, JSON errors, every CONTRACT §8 endpoint
except `/api/export/sheet06` which returns 404). Added `run_app.bat`.
**Result:** Server boots and returns valid JSON for every endpoint; custom events are analysed from the airport's own
monthly row; the bad writer contains the fabricated "20 points"; the smoke test later reached 15/15.
**Anomalies:** None during the endpoint tests after one fix: `/api/detector/airport` initially forced 2025-12 and
was changed to the latest flagged month (Hailing → 2025-08, unusual, 2 signals).
**AI:** DeepSeek Harness — wrote the pipeline, QA and server.

## 2026-10-24 00:45 — Phase 1: workbook fixtures and offline template writer

**Setup:** Generated `fixtures/mock_bootstrap.json` (8 airports, 5 events, 12 rules, 15 tests, 3 feedback seeds,
DQ001–004), `mock_detector_ranking.json` (192 airport-months; flags_own **12**; any-signal **13**; signal counts
`{0:179,1:11,2:1,3:1}`; Hailing 2025-07 −15.62 pp / 2025-08 −10.99 pp; Yunchuan 2025-07 YoY −0.80 pp; missing-weather
rows per ERRATA: Qinglan 2025-03, Gaoyuan 2025-09, Hailing 2025-11, Linjiang 2025-11), `mock_chart.json` (24 months,
Hailing/Yunchuan + peer line) and `mock_factsheets.json` (EVT001–EVT005). Wrote `engine/writer.py`: 17 fields with
English + Chinese labels, three distinct audience drafts, `[FACT: source]` / `[ASSUMPTION]` / `[UNKNOWN]` / `[HUMAN]`
tags, only fact-sheet numbers, `模拟` in f13–f15/f17, feedback matches quoted in f10, and `bad` mode that injects the
fabricated "20 points". Rendered `fixtures/output_EVT001.json` and `fixtures/output_bad.json` with the real writer.
**Result:** EVT001 renders 17 fields with risk Medium and three different messages; the bad output contains the
fabricated number for the checker demo. Fixture counts match Appendix A of the execution plan.
**Anomalies:** The fixture generator used the bundled build-time Python (openpyxl); the app never imports openpyxl.
**AI:** DeepSeek Harness — generated the fixtures and wrote the writer.

## 2026-10-24 00:40 — Setup for the unattended build: branch, merge, venv, port 8803

**Setup:** Read `README.md`, `ROLES.md`, `CONTRACT.md`, `docs/planning/ERRATA.md` and `EXECUTION_PLAN.md` §3/§9.
`git status` showed no changes to tracked files (only two untracked planning notes, which are not part of this
build). `git switch jonathan` succeeded (the repo had a local `Jonathan`; Git resolved it to the same ref) and
`git merge origin/main` reported "Already up to date" — `main` at `f70aecf` is an ancestor of the branch. Python is
**3.12.10**; there was no `.venv`, so I created one and ran `.venv\Scripts\python -m pip install -r requirements.txt`.
Port **8803 was free**, so the default port is 8803 (no `T3_PORT` override needed).
**Result:** The build can proceed; the app itself needs only the standard library. Fixtures are generated from
`Track 3 Data.xlsx` with the machine's bundled `openpyxl` (build-time only), so the runtime does not depend on the
pip install.
**Anomalies:** The pip install made no progress for ~20 minutes and was cancelled — PyPI is unreachable from this
network; `.venv` therefore has no third-party packages (fine for the app). `git fetch origin` and `git ls-remote`
failed twice with "connection reset"/timeout to `github.com:443`, while `https://api.github.com` answered 200; there
is no `gh` CLI and Git Credential Manager holds no GitHub credential, so a remote push may need the API route.
**AI:** DeepSeek Harness — executed the setup commands and wrote this entry.
