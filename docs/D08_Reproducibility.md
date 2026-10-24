# D08 — Reproducibility package (T3 Ops Copilot)

**模拟 / SIMULATED.** Every airport, event and number in this project is organizer-generated fiction.

This page lets a judge reproduce the prototype (D02) from a fresh clone on a clean machine. The root
[`../README.md`](../README.md) is the judge-facing run guide; this file records the exact environment and the
verification run of 2026-10-24.

## 1. Environment

| Item | Value |
|---|---|
| OS used for verification | Windows (PowerShell), repo at the local path `t3-copilot` |
| Python | 3.12.14 (`C:\Users\jonat\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe`); Python 3.10+ is required |
| Third-party packages needed by the app/engine/tests | **none** — Python standard library only |
| Network / API key needed | **none** — the default writer is offline |
| Repo `.venv` | Python 3.12.10, no third-party packages; PyPI was unreachable from the build laptop |
| `openpyxl` (optional build step only) | 3.1.5 in the bundled Python above; not required to run the app |
| Branch verified | `jonathan` |

`requirements.txt` contains build-time-only packages: `openpyxl` (workbook export), `pandas` (independent detector
cross-check), `Pillow` (chart image). The app never imports them.

## 2. Fresh-clone steps

All commands are run from the repo root.

```bash
# 1. (optional) rebuild data — needs openpyxl; skip if unavailable
python scripts/build_data.py

# 2. start the web app (stdlib only)
python app/server.py          # http://127.0.0.1:8803, or set T3_PORT for another port
#    Windows double-click equivalent: run_app.bat

# 3. unit tests (stdlib only)
python -m unittest discover -s tests

# 4. exam through the same pipeline the website uses (stdlib only)
python tests/run_tests.py --writer-mode offline
```

`.env.example` documents the reserved live-LLM settings (`T3_LLM_*`); this build does not call a live model, and
no key is needed for any step above. Never commit a real key.

## 3. Observed results of the verification run (2026-10-24)

### Data (optional)

```
Exported validated workbook: {'baseline': 192, 'weather': 192, 'events': 5, 'rules': 12, 'feedback_seed': 3,
 'tests': 15, 'field_defs': 10, 'data_quality': 4, 'checklist': 8, 'airports': 8, 'airport_names': 8}
```

`data/track3.json` regenerated **byte-identically** (same SHA-256 before and after) and the git working tree was
unchanged, so this step is not needed to run the app.

### Web app

```text
T3 OPS COPILOT - SIMULATED - http://127.0.0.1:8803
Press Ctrl+C to stop.
```

`GET /api/health` (observed) returned:

```json
{"ok": true, "engine": "ready", "writer_mode": "offline", "llm_configured": false,
 "checker_available": false, "runner_available": true, "sim_label": "模拟 / SIMULATED"}
```

`GET /` returned HTTP 200. Analysing EVT001–EVT005 through the pipeline behind `/api/analyze` returned
`engine_mode: "real"`, 17 non-empty fields and 3 distinct audience drafts per event; risk labels: EVT001 `Medium`,
EVT003 `Can't tell`, the rest `Low`. `POST /api/analyze` was also called directly for EVT001 and EVT003.

### Unit tests

```text
Ran 16 tests in 0.229s
OK
```

### Exam

```text
Exam: 0/21 passed; output written to exports\test_results.json
```

Exit code `1`; JSON summary official `0/15`, own `0/5`, negative `0/1`. **This is expected before the checker
merge:** the checker (`engine/checker.py`, 21 cases all gated on its result) is on `origin/ziyu`, not on this
branch. 20 cases fail only with `pipeline checker did not pass`; the fabricated-number negative case fails with
`bad writer was not blocked`. The small writer/pipeline fixes in `docs/planning/UPDATE_PLAN_2026-10-24.md` must
also be applied, then the exam re-run and the results updated — no pass rate is claimed here.

### Detector truth

192 airport-months; 12 own-history flags; 13 any-signal; signal counts `{0: 179, 1: 11, 2: 1, 3: 1}`;
Hailing 2025-07 = −15.62 / −5.46 / −11.48 pp; Hailing 2025-08 = −10.99 / −3.66 / −9.14 pp; Yunchuan 2025-07 =
−6.07 pp own, −0.80 pp YoY. These match the organizer workbook (`docs/NUMBERS.md`, `EXECUTION_PLAN.md`
Appendix A).

## 4. Data placement

| Path | Role |
|---|---|
| `Track 3 Data.xlsx` | Organizer workbook, read-only; the only real input |
| `data/track3.json` | Committed export of the workbook; the app's runtime data source |
| `data/feedback_seed.json` | Committed organizer feedback seeds (accept / edit / reject) |
| `data/feedback.jsonl` | Append-only log written by the app when a reviewer saves a decision; created on first use |
| `fixtures/*.json` | Committed generated JSON used as the pipeline fallback (and by the detector list endpoints on this branch) |

Do not edit `Track 3 Data.xlsx`; do not edit `data/track3.json` by hand. Rebuild with `scripts/build_data.py`
instead.

## 5. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Address already in use` on 8803 | Another instance is running; set `T3_PORT=8814` (or any free port) before starting |
| `checker_available: false`, panel says "not checked" | Expected before the checker merge; the app deliberately does not fake a pass |
| Exam reports 0/21 | Same missing checker (see §3); after merging `engine/checker.py` from `origin/ziyu`, re-run the exam |
| `ModuleNotFoundError: openpyxl` on `scripts/build_data.py` | Build-time dependency only. Skip the rebuild (the committed JSON works), or use a Python environment with `openpyxl` installed |
| Chinese text garbled in a Windows console | Write output to a file or open it in the browser; set `PYTHONIOENCODING=utf-8` (the `.bat` files do this) |

## 6. What this package does not include / limits

- All data is simulated (`模拟`); there is no real-world operational data, no live flight/crew/gate data and no
  network feed.
- The default offline template writer is the only writer enabled in this build; the optional live LLM was cut to
  fit the schedule.
- The checker is not merged on this branch, so checker-gated claims (exam pass rate, bad-AI block) are pending.
- No API keys are committed (`.env` is git-ignored). The hostile-input test cases use an invented name and phone
  number as test data; the writer's output redacts them.
