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

## 2026-10-24 03:05 — Checker built: all 13 rules C01-C13 block on cue and pass on a good output

**Setup:** On branch `ziyu`, merged `origin/main` (fast-forward to 396598b; a locked `docs/planning/R1-R3_EXPLAINED.pdf` blocked the merge until the viewer was closed — the file was moved aside, merged back byte-identical, backup kept in the opencode temp folder). Implemented `engine/checker.py` (`check(output, facts) -> {"passed", "checks", "failures"}`) per `docs/planning/agent_prompts/ziyu.md`: C01-C13, each failure names the offending text; masks IDs (SIM-\*, RULE/EVT/TEST/REC ids, Fxx), dates (incl. Chinese dates and bare years), times, field keys and list numbering before C02 number matching (tolerance 0.01). Jonathan's `fixtures/output_*.json` do not exist, so `tests/test_checker.py` builds the good and bad outputs inline in the CONTRACT §6 "output" shape from Jason's real `fixtures/factsheet_EVT001.json` / `EVT003.json`, using only numbers from their "numbers" lists; the bad output uses "20 points" (CONTRACT §11 bad-writer mode). The checker also accepts a full pipeline payload `{"output": ...}` and a whole fact sheet and unwraps both.
**Result:** `python -m unittest tests.test_checker -v` ran 16 tests: OK (good EVT001 + conflict-EVT003 outputs pass every check; the bad output fails only C02 and names "20" and f05; one failing example per check C01, C03-C13, each failing exactly its own check; plus hedged-causation and disclosed-missing-weather positive controls). `python -m unittest discover -s tests -v` ran 32 tests: OK (16 new + 16 pre-existing, no regressions).
**Anomalies:** BLOCKED (not mine to fix): `tests/run_tests.py` still exits 2 with `pipeline not available` because `engine/pipeline.py` (Jonathan) is absent — unchanged from Jason's log. Note for Jonathan's writer: C02 is deliberately strict — e.g. "own 12-month average" would trip it because 12 is not whitelisted (Jason's fact texts say "own average"); use the fact-sheet phrasing, and quote feedback without rec ids or via words (rec ids are masked, "12" is not). The C10 failing example uses a fact sheet with an appended weather-missing entry because no EVT001-EVT005 fixture has one.
**AI:** OpenCode (GLM-5.3) implemented the checker and tests unattended from the ziyu.md prompt; I reviewed the spec compliance (mask list, tolerance, "20 points" negative case) and kept the good/bad inline outputs number-clean against both fact sheets.
