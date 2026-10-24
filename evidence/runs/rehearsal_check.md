# Rehearsal check — demo-script dry run

> 模拟 / SIMULATED — fictional airports, events and numbers from the organizer workbook. This is
> a scripted, offline dry run of the live-demo beats in `docs/D01_Presentation_Outline.md`;
> no browser and no API key were needed.

**When:** 2026-10-24 21:22 China time (UTC+8).
**How:** a throwaway script (kept outside the repo) imported `engine.pipeline` from the repo root
and ran the six demo beats below in order, then the exam CLI
(`python tests/run_tests.py --writer-mode offline`). Every result in the table is the value the
run actually printed; nothing was written in advance. The raw machine output stands behind each
row: the engine calls (headless) and the exam JSON.

| # | Step | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | `analyze("EVT001")` | risk Medium; `check.passed` True | risk Medium; `check.passed` True | PASS |
| 2 | `analyze(custom Hailing event)`: 14:00, "heavy rain and gusts next 6 h", "busy afternoon" | custom event analyzed; `check.passed` True | risk Medium; `check.passed` True | PASS |
| 3 | `run_bad_writer_demo("EVT001")` | blocked True; C02 failure | blocked True; failures `['C02']` | PASS |
| 4 | `analyze("EVT003")` | risk "Can't tell" | risk Can't tell | PASS |
| 5 | `analyze("EVT005")` | first action "confirm current resources" | first_action "confirm current resources" | PASS |
| 6 | `python tests/run_tests.py --writer-mode offline` | 21/21 | pass 21/21; official 15/15; own 5/5; negative 1/1 | PASS |

**Notes for whoever runs the demo:**
- Step 2 is the "type a new event" beat (0:25–1:15): the writer and checker hold up on a typed
  event, not only on organizer events.
- Step 3 is the bad-AI demo (2:45–3:20): the block names the fabricated number via C02; the
  fallback output is marked for human review.
- The exam summary (15 official + 5 own + 1 negative) matches the committed
  `exports/test_results.json` from the gate run.
