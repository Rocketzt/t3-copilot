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
