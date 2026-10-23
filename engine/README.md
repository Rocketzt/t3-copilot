# engine/ — the assistant's core

**Owners (see `ROLES.md`):** Jason — `data`, `detector`, `rules`, `facts`, `feedback`. Ziyu — `checker`.
Jonathan — `writer`, `pipeline`. Module APIs and JSON shapes are fixed in CONTRACT §3–§6.

| Module | Job |
|---|---|
| `data.py` | Load `Track 3 Data.xlsx` (or `data/track3.json`) into plain dicts; fail loudly on a missing sheet or column |
| `detector.py` | Three comparisons, signals, verdict, confidence, ranking, `airport_context`, chart series |
| `rules.py` | RULE001–012 trigger predicates, deterministic, no LLM |
| `facts.py` | Fact sheet: facts with source IDs, a numbers whitelist, assumptions, unknowns, risk |
| `writer.py` | Template writer (offline), LLM writer (optional) and `bad` mode for the checker demo |
| `checker.py` | Blocks untraceable numbers, committed actions, PII, causal claims and missing `模拟` labels |
| `feedback.py` | Append-only `data/feedback.jsonl`, seeded from sheet 07 |
| `pipeline.py` | `analyze()`, `ask()` and the JSON the API returns |

Rule: code computes every number; the writer only turns facts into prose.
