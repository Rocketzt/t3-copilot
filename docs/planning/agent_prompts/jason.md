# Agent prompt — Jason (data, detector, rules, fact sheet, feedback, tests)

## Tonight: the one prompt to paste

Before you start:
1. If you have the ClawsGO cross-check files (CSV, report, chart, script), copy them into the repo folder
   `evidence/ai/clawsgo/`.
2. Open a terminal in the repo folder and start your agent (for example `claude`).
3. Paste the box below. It gets everything ready, then runs the full build prompt further down this file.
4. Let it run. Allow it to edit files and run commands without asking each time.

````text
Get this repo ready, then do tonight's build. Work unattended; do not wait for me.

SETUP (stop and write down the reason if any step fails; never discard my files or force anything)
1. Run `git status`. If there are uncommitted changes to tracked files, STOP and tell me what they are.
2. Run `git fetch origin`. Then switch to my branch with `git switch jason` (if it does not exist locally:
   `git switch -c jason --track origin/jason`). Then run `git merge origin/main`. If the merge has conflicts,
   run `git merge --abort`, STOP and tell me.
3. Check that `python --version` is 3.10 or newer. Create a virtual environment if `.venv` is missing:
   `python -m venv .venv`. Install packages with the venv's own Python:
   - Windows: `.venv\Scripts\python -m pip install -r requirements.txt`
   - Mac/Linux: `.venv/bin/python -m pip install -r requirements.txt`
   Use that Python for every command from now on. Confirm that `import openpyxl, pandas` works.
4. Check that these exist: `Track 3 Data.xlsx` (repo root), ROLES.md, CONTRACT.md, EXECUTION_PLAN.md,
   docs/planning/ERRATA.md. If any is missing, STOP and tell me.
5. If `evidence/ai/clawsgo/` contains files, commit only that folder: `git add evidence/ai/clawsgo`, then
   `git commit -m "Add raw ClawsGO detector cross-check output"`. Do not edit those files.
6. Add a short "Setup" entry at the top of docs/project/log/jason.md, using the format in that file: Python
   version, packages installed, the commit you merged from main, and whether the ClawsGO files were present.
   Commit it.

BUILD
7. Open docs/planning/agent_prompts/jason.md. Follow the prompt in the SECOND box (the one starting "You are working
   unattended…") exactly as if I had pasted it to you: Phases 1–3, then FINISH. Its HARD RULES apply to everything
   you do, including the file list you may edit and "never push to main".
8. At the very end, run `git push origin jason` and print a 5-line summary:
   - which phases finished;
   - the test results;
   - anything BLOCKED or FAILED;
   - the commands I should run in the morning to check.
````

## The full build prompt (used by step 7 above)

Copy everything inside the box into your agent, in the repo root, on branch `jason`.

````text
You are working unattended in the git repo "t3-copilot" (HackSHSID 2026, Track 3). You are on branch `jason`.
Work through Phases 1–3 in order. Do not wait for me. If something blocks you, write it down and move on to the
next item you can do. Do not guess.

READ FIRST: README.md, ROLES.md, CONTRACT.md (§2–§6 and §9), docs/planning/ERRATA.md, EXECUTION_PLAN.md §4 and §8.

HARD RULES
- Edit ONLY these files:
  - scripts/build_data.py, scripts/crosscheck_detector.py
  - data/track3.json, data/feedback_seed.json
  - engine/__init__.py, data.py, detector.py, rules.py, facts.py, facts_risk.py, feedback.py, i18n.py
  - tests/* (any file except tests/test_checker.py, which is Ziyu's)
  - fixtures/factsheet_*.json
  - docs/NUMBERS.md, docs/test_specs.md
  - docs/project/log/jason.md
  Never edit other files, especially CONTRACT.md, EXECUTION_PLAN.md and "Track 3 Data.xlsx" (read-only input).
- Runtime code uses only the Python 3.10+ standard library. openpyxl is allowed only in scripts/build_data.py and
  pandas only in scripts/crosscheck_detector.py. Install them in a virtual environment with
  `python -m pip install -r requirements.txt`.
- Where CONTRACT.md and docs/planning/ERRATA.md disagree, ERRATA.md wins. In particular:
  - the missing weather rows are 青岚机场 2025-03, 高原机场 2025-09, 海陵国际机场 2025-11 and 临江机场 2025-11;
  - RULE003 fires on the own-history signal only (ERRATA C7);
  - RULE007 fires only on the decision words 取消/放行/调度/维修/赔付 and cancel/release/dispatch/maintenance/
    compensation (ERRATA C8). Field 12 still always lists the human decisions.
- Set PYTHONIOENCODING=utf-8. Write every file as UTF-8. Never print raw Chinese to the console when a file will do.
- Never invent a number. Every number must come from the workbook or be computed from it. If a check fails, report
  the real output.
- Commit after each phase with a clear message ending in "Assisted-by: <your agent name>". Then run
  `git push origin jason`. Never push to main and never merge.

PHASE 1 — data + detector (most important)
1. scripts/build_data.py: read the workbook (sheet names as in CONTRACT §2) and write data/track3.json and
   data/feedback_seed.json (the 3 rows of sheet 07). Use the row keys from CONTRACT §3, assert the counts, and fail
   loudly if a sheet or column is missing.
2. engine/data.py: `load_data()` reads data/track3.json and returns the Data object from CONTRACT §3.
3. engine/detector.py: `compute_all`, `ranking`, `airport_context`, `chart_series`, `summary`, exactly as in
   CONTRACT §4.
   - own = column I;
   - peer = (E − G) × 100;
   - yoy = (E 2025 − E 2024, same month) × 100;
   - a signal is ≤ −5.00 pp.
   airport_context must report the month it picked and why ("selection_reason") — ERRATA C9.
4. tests/test_detector.py: a stdlib unittest that asserts ALL of these, with a tolerance of 0.02 pp:
   - 192 rows; 12 rows with own ≤ −5.00, 11 of them in July or August;
   - signal counts {0: 179, 1: 11, 2: 1, 3: 1};
   - 海陵国际机场 2025-07: own −15.62, peer −5.46, yoy −11.48, 3 signals;
   - 海陵国际机场 2025-08: own −10.99, peer −3.66, yoy −9.14, 2 signals;
   - 云川国际机场 2025-07: own −6.07, peer +5.47, yoy −0.80, 1 signal;
   - 北岭机场 2025-12: own −4.74, yoy −5.59, 1 signal;
   - weather_missing is true for exactly the 4 rows in the rules above.
   Run it: `python -m unittest tests.test_detector -v`. Paste the real result into your log.
5. docs/NUMBERS.md: a short table of the canonical numbers (the ones above, plus the network monthly averages),
   generated by a small script from the detector output, not typed by hand. Label it "模拟 / SIMULATED".
Commit and push.

PHASE 2 — rules, fact sheet, feedback
6. engine/rules.py: `evaluate(data, event, context)` and `all_rules(data)` as in CONTRACT §5, with the ERRATA
   changes. Deterministic; no LLM.
7. engine/facts.py (+ facts_risk.py if useful): build the "facts" object from CONTRACT §6:
   - facts with source IDs;
   - the numbers whitelist;
   - assumptions, unknowns, missing_data, forbidden_actions, sources;
   - risk, conflict, pii_redacted, feedback_matches, sim_label.
   Expected results: EVT001 → risk Medium; EVT003 → "Can't tell" with conflict=true; EVT005 with the seed rejection
   → lowered risk and first action "confirm current resources". Redact phone numbers, ID numbers and emails from
   any input text.
8. engine/feedback.py: an append-only data/feedback.jsonl. Provide load_records, append_record and match, as in
   CONTRACT §6. Seeds come from data/feedback_seed.json; never modify or delete a record.
9. Write fixtures/factsheet_EVT001.json … factsheet_EVT005.json from the real code. Jonathan's UI and writer use
   them.
10. tests/test_facts.py: unittests for steps 6–8 covering the expected results above, a PII redaction case, and the
    feedback append-only property. Run them and log the real results.
Commit and push.

PHASE 3 — exam runner + cases (CONTRACT §9, EXECUTION_PLAN §8)
11. docs/test_specs.md: plain-English must / must-not for TEST001–TEST015 (from sheet 08), our 5 own events, the
    hostile input and the fabricated-number negative test. Use EXECUTION_PLAN §8.3 and Appendix C.
12. tests/cases_official.py, tests/own_events.py, tests/runner.py, tests/run_tests.py:
    - the runner calls engine.pipeline.analyze()/ask(). Jonathan owns pipeline.py.
    - If engine.pipeline does not exist or fails to import, the runner must print "pipeline not available" and exit
      with code 2. It must NOT fake results.
    - Prove that the runner's grading logic works with a small fake pipeline that lives only in
      tests/test_runner_selfcheck.py.
13. If evidence/ai/ contains Jason's ClawsGO cross-check CSV, write scripts/crosscheck_detector.py to compare it
    row by row with detector.compute_all() (tolerance 0.02 pp) and write exports/crosscheck_detector.md. If it is
    not there, skip this step and say so in the log.
Commit and push.

FINISH
Add an entry at the top of docs/project/log/jason.md using the format in that file. Include:
- what was done per phase;
- the exact commands to re-run each check and their real results;
- anything BLOCKED or FAILED;
- an "AI:" line naming the agent.
Commit and push one last time.
````
