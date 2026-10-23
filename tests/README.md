# tests/ — the exam (Part 3)

**Owner:** Jason — the runner, the cases and the plain-English specs in `docs/test_specs.md` (see `ROLES.md`).

- `runner.py` / `run_tests.py`: run every case through the same `engine.pipeline` the website uses (no answer bank).
  Run with `python tests/run_tests.py --writer-mode offline --out exports/test_results.json`.
- `cases_official.py`: TEST001–TEST015 from sheet 08.
- `own_events.py`: our 5 unseen events, the hostile input and the fabricated-number negative test.

A test passes only if every *must* is present, no *must-not* matches and the answer's own checker passes. Keep the
first full run (`exports/test_results_run1.json`) and report its real pass rate.
