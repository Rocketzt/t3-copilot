# Work log — Jason (evidence and delivery)

Only Jason edits this file, so it never conflicts on merge. Newest entry first, written the same day as the work.
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

## 2026-10-24 16:31 — Hostile operational request is neutralized in the fact sheet

**Setup:** Confirmed no tracked changes, fetched origin, switched to `jason`, and pulled `origin/jason` (already up to date). Changed the fact builder to replace event text containing RULE007 decision words with a neutral professional-review notice in the displayed event and sourced facts, while checking the original redacted text for rules. Added an OWN005 regression test and regenerated EVT001–EVT005 fixtures; none changed.
**Result:** `.venv\Scripts\python.exe -m unittest discover -s tests -v` ran 19 tests: OK. The OWN005 fact sheet contains neither `cancel flight` nor `weather caused it`, still redacts PII, and still fires RULE007. `git diff --check` exited 0. Exam score: unavailable; `.venv\Scripts\python.exe tests/run_tests.py --writer-mode offline` printed `pipeline not available`, so no exam cases or score were produced.
**Anomalies:** BLOCKED: `engine/pipeline.py` is absent on `jason`; the offline exam cannot run to completion. Pre-existing untracked exports and script were left untouched.
**AI:** Codex updated fact presentation, added the regression test, checked the fixture output, and recorded the actual test and exam results.

## 2026-10-24 16:18 — Fact sheets whitelist detector signals and event-text numbers

**Setup:** Confirmed no tracked changes, fetched origin, switched to `jason`, and pulled `origin/jason` (already up to date). Added each quoted detector month's signal count to its SIM-BASE fact and number list, and added Arabic numeric literals from sanitized `weather_text`, `ops_text`, `known`, `unknown`, and `notes` with the event ID as source. Regenerated the five EVT001–EVT005 fact-sheet fixtures.
**Result:** `.venv\Scripts\python.exe -m unittest discover -s tests -v` ran 18 tests: OK, including new tests for every quoted detector month and all five event-text fields. `git diff --check` exited 0.
**Anomalies:** None. Pre-existing untracked exports and script were left untouched.
**AI:** Codex updated the fact builder, added regression tests, regenerated fixtures, and checked the test and diff results.

## 2026-10-24 16:15 — ClawsGO cross-check agrees; D05 and D03 prepared

**Setup:** Fetched origin, stayed on `jason`, and fast-forwarded to `origin/main` at 396598b. Extracted five zip files into `evidence/ai/clawsgo/crosscheck/`, verified their staged bytes against the extracted files, removed the requested zip, and committed that folder. Added `scripts/crosscheck_detector.py` and its generated report, then wrote D05 and the D03 skeleton in separate commits.
**Result:** `.venv\Scripts\python.exe scripts/crosscheck_detector.py` exited 0: 192 CSV rows checked against 192 detector rows, 0 mismatches at 0.02 pp tolerance; the report includes the top 10 and the agreement note. D05 records all three organizer seeds, append-only recall, the EVT005 Gaoyuan result, and an empty live-record section. D03 lists 15 official cases and six own/negative cases; all 21 Result and Evidence cells are empty, verified by a local structure check.
**Anomalies:** BLOCKED: `engine/pipeline.py` is not merged, so D03 has no exam results or human scores and D05 has no live app records. The other pre-existing untracked files were not changed.
**AI:** Codex wrote the comparison script and report, checked the seed and fixture values for D05, and prepared the D03 tables without inventing results.

## 2026-10-24 01:13 — Fact sheets now whitelist all comparison and weather numbers

**Setup:** Pulled `origin/jason` (already up to date). Added peer and available YoY gaps to each SIM-BASE month fact and number whitelist; added a selected-month SIM-WEATHER fact with precipitation, max wind, and bad-weather days, or an explicit missing-data fact without weather numbers. Redacted Chinese names after `旅客`. Regenerated the five `fixtures/factsheet_EVT001..005.json` files.
**Result:** `.venv\Scripts\python.exe -m unittest tests.test_facts -v` ran 9 tests: OK. `.venv\Scripts\python.exe -m unittest discover -s tests -v` ran 16 tests: OK. `git diff --check` exited 0.
**Anomalies:** The separate exam command `.venv\Scripts\python.exe tests/run_tests.py --writer-mode offline --out exports/test_results.json` still printed `pipeline not available` and exited 2 because `engine/pipeline.py` is absent; no exam result was written. Existing untracked files were untouched.
**AI:** Codex added the source-backed facts and regression tests, then regenerated fixtures from the implementation.

## 2026-10-24 00:14 — Build hand-off complete with exam integration pending

**Setup:** Phase 1 exported and validated the organizer workbook, implemented the detector, and generated `docs/NUMBERS.md`. Phase 2 implemented deterministic rules, source-backed fact sheets, PII redaction, append-only feedback, and five real event fixtures. Phase 3 added the 15 official cases, five own cases, negative test, exam runner, and `docs/test_specs.md`.
**Result:** From the repo root, set `PYTHONIOENCODING=utf-8` and rerun: `.venv\Scripts\python.exe scripts/build_data.py` (192 baselines, 192 weather rows, 5 events, 12 rules, 15 tests); `.venv\Scripts\python.exe -m unittest tests.test_detector -v` (4 tests, OK); `.venv\Scripts\python.exe -m unittest tests.test_facts -v` (5 tests, OK); `.venv\Scripts\python.exe -m unittest tests.test_runner_selfcheck -v` (3 tests, OK); `.venv\Scripts\python.exe -m unittest discover -s tests -v` (12 tests, OK).
**Anomalies:** BLOCKED: `.venv\Scripts\python.exe tests/run_tests.py --writer-mode offline --out exports/test_results.json` printed `pipeline not available` and exited 2 because `engine/pipeline.py` is absent; no real exam pass rate exists yet. SKIPPED: no ClawsGO CSV under `evidence/ai/`, so no optional detector cross-check report was made. No other final test failures.
**AI:** Codex implemented and verified these phases. The self-check fake pipeline is limited to `tests/test_runner_selfcheck.py` and is not an exam result.

## 2026-10-24 00:13 — Phase 3 runner ready; integration run blocked

**Setup:** Mapped all 15 workbook TEST IDs to English acceptance checks, added five own events plus the fabricated-number negative case, and built the exam runner against `engine.pipeline.analyze()/ask()`.
**Result:** `python -m unittest tests.test_runner_selfcheck -v` ran 3 tests: OK. `python tests/run_tests.py --writer-mode offline --out exports/test_results.json` printed `pipeline not available` and exited 2, as required. No exam result file or pass rate was fabricated.
**Anomalies:** `engine/pipeline.py` is not present on this branch, so the real 15 official and five own cases cannot run yet. `evidence/ai/` contains no ClawsGO CSV, so the optional cross-check was skipped.
**AI:** Codex implemented the runner and specifications; the fake pipeline was used only in the runner self-check.

## 2026-10-24 00:10 — Phase 2 fact sheets and feedback verified

**Setup:** Added deterministic RULE001–012 evaluation, source-backed facts and risk, PII redaction, append-only feedback, and five generated EVT fact-sheet fixtures.
**Result:** `python -m unittest tests.test_facts -v` ran 5 tests: OK. EVT001 is Medium; EVT003 is Can't tell with conflict; EVT005 is Low after the seed rejection and first checks current resources.
**Anomalies:** Initial test run had a false `pii_redacted` flag and a sandbox temp-path permission error. Both were fixed; the final run passes.
**AI:** Codex implemented and checked this phase against the contract and organizer seeds.

## 2026-10-24 00:06 — Phase 1 detector matches workbook checks

**Setup:** Exported all required workbook sheets with `python scripts/build_data.py`; generated `data/track3.json`, `data/feedback_seed.json`, and `docs/NUMBERS.md` from detector output.
**Result:** `python -m unittest tests.test_detector -v` ran 4 tests: OK. Verified 192 airport-months, 12 own-history flags, 13 any-signal flags, signal counts 179/11/1/1, and the four missing-weather rows.
**Anomalies:** None.
**AI:** Codex implemented the export, detector, generated numbers, and tests; kept workbook values as the source of numeric claims.

## 2026-10-23 23:52 — Setup completed on jason

**Setup:** Merged origin/main at f70aecf. Python 3.12.8 in .venv; installed requirements.txt with openpyxl 3.1.5, pandas 3.1.0, and Pillow 13.0.0. Confirmed openpyxl and pandas import. All required source documents and workbook are present.
**Result:** Ready for Phases 1–3. No files were present in evidence/ai/clawsgo, so there was no raw ClawsGO commit.
**Anomalies:** Four untracked prompt copies blocked the first merge attempt. Moved them to ../agent_prompts_backup, then merged. The copies match the earlier 63325b6 prompts; only jason.md is older than the merged version.
**AI:** Codex handled setup and verified the backup against Git blob hashes.
