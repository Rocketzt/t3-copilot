# Work log — Ziyu (engine and AI core)

Only Ziyu edits this file, so it never conflicts on merge. Newest entry first, written the same day as the work.
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

## 2026-10-24 22:11 — Pre-submission tidy-up: clean-clone of the public repo reproduces every result

**Setup:** Merged `origin/main` into `ziyu` (fast-forward, no conflicts). Got the fresh numbers for this session: `python -m unittest discover -s tests` ran 56 tests OK; `python tests/run_tests.py --writer-mode offline` reported exam 21/21 (official 15/15, own 5/5, negative 1/1); `pipeline.run_bad_writer_demo('EVT001')` returned blocked `True` with failure C02. Clean-clone check in an outside temp folder:
| # | Command (in the clone) | Result |
|---|---|---|
| 1 | `git clone https://github.com/Rocketzt/t3-copilot.git` | OK (first two attempts: "Connection was reset", this PC's network; third attempt clean) |
| 2 | `python -m venv .venv` | OK — Python 3.13.11, pip 25.3 |
| 3 | `.venv\Scripts\python.exe -m pip install -r requirements.txt` | OK — installed Pillow 13.0.0, openpyxl 3.1.5, pandas 3.1.0 (+ numpy etc.); PyPI reachable |
| 4 | `.venv\Scripts\python.exe -m unittest discover -s tests` | `Ran 56 tests in 0.771s` — OK |
| 5 | `.venv\Scripts\python.exe tests/run_tests.py --writer-mode offline` | `Exam: 21/21 passed; output written to exports\test_results.json`, exit 0 |
| 6 | `.venv\Scripts\python.exe -u app/server.py` (`T3_PORT=8817`) | banner `T3 OPS COPILOT - SIMULATED - http://127.0.0.1:8817`; `GET /` → 200 (16,473 bytes); `GET /api/health` → 200 `{"ok": true, "engine": "ready", "writer_mode": "offline", "llm_configured": false, "checker_available": true, "runner_available": true, "sim_label": "模拟 / SIMULATED"}`; server stopped after the check |
**Result:** The public repo reproduces itself from a clean clone exactly as `README.md` says: 56/56 unit tests, 21/21 exam, the app boots offline with the checker available. No README run-step was wrong or missing for a machine without a system proxy.
**Anomalies:** On this PC (a system proxy is configured in Windows settings, not in environment variables) plain `urllib` requests to `http://127.0.0.1:*` from a fresh interpreter were answered with `RemoteDisconnected` because the proxy intercepted localhost; `curl.exe --noproxy *` and the browser got clean 200s. Appended a one-line note to README's health block so nobody mistakes this for an app defect. A pre-existing process (not started by this run) was listening on 8803 and was left untouched; the clone server ran on 8817 instead.
**AI:** OpenCode (GLM-5.3) — ran the clone check unattended and recorded only observed output; no repo file outside the allowed list was touched.

## 2026-10-24 21:24 — D01 path fix + demo rehearsal checked: all six beats pass

**Setup:** Merged `origin/main` into `ziyu` (fast-forward, no conflicts). Changed only the two `../exam_now.json` references in `docs/D01_Presentation_Outline.md` to `exports/test_results.json`. Ran a throwaway script kept outside the repo (temp folder): `engine.pipeline.analyze()` on EVT001, a typed Hailing event ("14:00, heavy rain and gusts next 6 h, busy afternoon"), `run_bad_writer_demo("EVT001")`, EVT003, EVT005, then `python tests/run_tests.py --writer-mode offline`. Saved the observed results to `evidence/runs/rehearsal_check.md` (21:22 China time).
**Result:** Six of six demo beats PASS with real values: EVT001 risk Medium / check passed; typed event risk Medium / check passed; bad-writer demo blocked with C02; EVT003 Can't tell; EVT005 first action "confirm current resources"; exam 21/21 (15 official + 5 own + 1 negative).
**Anomalies:** None for the run. Note: an earlier D04 draft I started was cancelled by the team before commit; nothing of it remains in the tree.
**AI:** OpenCode (GLM-5.3) ran the rehearsal script unattended and wrote the evidence table only from values it actually observed; D04/D06/D07 were left untouched (Jason's).

## 2026-10-24 03:36 — C02 false positive fixed: letters+digits identifiers no longer read as numbers

**Setup:** `git status` clean, `git pull origin ziyu` up to date (GitHub unreachable for ~4 min; retried until it connected). Replaced the fixed RULE/EVT/TEST/REC id mask in `engine/checker.py` with a general one, `(?i)\b[A-Za-z]{2,}[-_]?\d+\b`, so any identifier of letters directly followed by optional `-`/`_` and digits is masked before number extraction (RULE007, EVT001, TEST001, REC001, OWN002, MU123, CUSTOM-3). Bare numbers and numbers with units ("20 points", "6.5 mm", "-10.99 pp") are still never masked; SIM-* and Fxx/fxx masks unchanged. Added `test_c02_letters_digits_identifiers_are_masked`: text with "OWN002", "MU123" and "CUSTOM-3" passes C02 (and every other check), while "Hailing is 20 points below normal" still fails C02 only and names 20.
**Result:** `python -m unittest discover -s tests -v` ran 36 tests: OK (18 checker tests + 18 others, no regressions; the PII tests confirm pure-digit phone/ID numbers still fail C02).
**Anomalies:** The first four `git pull` attempts failed with github.com connection errors (network); the fifth succeeded with no changes.
**AI:** OpenCode (GLM-5.3) applied the general identifier mask and the two new test cases as specified; no other check was loosened.

## 2026-10-24 03:17 — C05 false positive fixed: "official airline and airport channels" now accepted

**Setup:** `git status` clean, `git pull origin ziyu` up to date (GitHub was unreachable for ~2 min; retried until it connected). Loosened only `_OFFICIAL_CHANNELS` in `engine/checker.py`: `official\s+(?:\w+\s+){0,3}channels`, so up to 3 words may sit between "official" and "channels"; Chinese alternatives unchanged; no other check touched. Added `test_c05_official_channels_phrase_flexibility` in `tests/test_checker.py`: "Please check official airline and airport channels for updates." passes C05 (and every other check), while a passenger message with no channels phrase still fails C05 only.
**Result:** `python -m unittest discover -s tests -v` ran 33 tests: OK (17 checker tests + 16 pre-existing, no regressions).
**Anomalies:** The first three `git pull` attempts failed with connection errors to github.com (network); the fourth succeeded with no changes.
**AI:** OpenCode (GLM-5.3) applied the one-pattern fix and the new test as specified; no other checks were loosened.

## 2026-10-24 03:05 — Checker built: all 13 rules C01-C13 block on cue and pass on a good output

**Setup:** On branch `ziyu`, merged `origin/main` (fast-forward to 396598b; a locked `docs/planning/R1-R3_EXPLAINED.pdf` blocked the merge until the viewer was closed — the file was moved aside, merged back byte-identical, backup kept in the opencode temp folder). Implemented `engine/checker.py` (`check(output, facts) -> {"passed", "checks", "failures"}`) per `docs/planning/agent_prompts/ziyu.md`: C01-C13, each failure names the offending text; masks IDs (SIM-\*, RULE/EVT/TEST/REC ids, Fxx), dates (incl. Chinese dates and bare years), times, field keys and list numbering before C02 number matching (tolerance 0.01). Jonathan's `fixtures/output_*.json` do not exist, so `tests/test_checker.py` builds the good and bad outputs inline in the CONTRACT §6 "output" shape from Jason's real `fixtures/factsheet_EVT001.json` / `EVT003.json`, using only numbers from their "numbers" lists; the bad output uses "20 points" (CONTRACT §11 bad-writer mode). The checker also accepts a full pipeline payload `{"output": ...}` and a whole fact sheet and unwraps both.
**Result:** `python -m unittest tests.test_checker -v` ran 16 tests: OK (good EVT001 + conflict-EVT003 outputs pass every check; the bad output fails only C02 and names "20" and f05; one failing example per check C01, C03-C13, each failing exactly its own check; plus hedged-causation and disclosed-missing-weather positive controls). `python -m unittest discover -s tests -v` ran 32 tests: OK (16 new + 16 pre-existing, no regressions).
**Anomalies:** BLOCKED (not mine to fix): `tests/run_tests.py` still exits 2 with `pipeline not available` because `engine/pipeline.py` (Jonathan) is absent — unchanged from Jason's log. Note for Jonathan's writer: C02 is deliberately strict — e.g. "own 12-month average" would trip it because 12 is not whitelisted (Jason's fact texts say "own average"); use the fact-sheet phrasing, and quote feedback without rec ids or via words (rec ids are masked, "12" is not). The C10 failing example uses a fact sheet with an appended weather-missing entry because no EVT001-EVT005 fixture has one.
**AI:** OpenCode (GLM-5.3) implemented the checker and tests unattended from the ziyu.md prompt; I reviewed the spec compliance (mask list, tolerance, "20 points" negative case) and kept the good/bad inline outputs number-clean against both fact sheets.
