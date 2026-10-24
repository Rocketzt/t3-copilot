# Screenshots — real captures of the running app

All files here are **real screenshots of the running T3 Ops Copilot app**, not mock-ups.
Captured by teammate `demo-evidence` with headless Edge 155 (CDP, `Emulation.setDeviceMetricsOverride`
1440×1000, deviceScaleFactor 1) against the Lead's server `http://127.0.0.1:8811`, after each page
finished its `/api/bootstrap` boot (and, for the result page, after the `?event=` analyze call returned).
Every file is exactly **1440×1000 px** PNG and shows the `模拟 / SIMULATED` badge.

- Phase A capture window: **2026-10-24 16:25–16:36 +0800**. `01`–`07` were shot last at
  16:35:16–16:35:55 against the final UI working tree (`app.js` 16:28:08, `index.html` 16:33:33);
  `08` was shot at 16:32:32 — the only later HTML change was the footer default/footer-only word,
  which is outside `08`'s visible region, so its content is unchanged.
- Code served: base commit `3d962de` + `ui-fixer`'s **uncommitted** `app/static/app.js` change
  (mtime 16:28:08) that added the `?tab=` / `?event=` deep links, the `engine:` badge fix,
  the single-`[ASSUMPTION]`-chip fix and the English tier fix. Lead confirmed these UI fixes as done.
- **Checker is still "not checked" on this branch** (`/api/health` → `checker_available: false`).
  The UI shows an honest "not checked" note, never a fake green. All checker evidence is
  therefore *interim* until the user merges `engine/checker.py`.

## Mapping — file → what it shows → checker-dependent?

| File | URL | What it shows | Checker-dependent? | Phase |
|---|---|---|---|---|
| `01-assistant.png` | `/` | Assistant default page: five organizer event cards (EVT001–EVT005), the "type a new event" form, `模拟 / SIMULATED` header, **`engine: real`** badge | **No** (no analyze run; picker + form only) | A |
| `02-detector.png` | `/?tab=detector` | Detector tab: 192 airport-months · 12 official RULE003 flags · 13 any-signal · 2 multi-signal · 1 three-signal; Hailing vs Yunchuan SVG chart with same-class peer line and 2025-07/08 highlight; ranking table (2025-07 Hailing −15.62 pp, 3 signals) | **No** (data from `/api/detector/ranking` + `/api/detector/chart`) | A |
| `03-exam.png` | `/?tab=exam` | Exam tab **initial state**: description, "Run exam" button, empty results area, "Download report (JSON)" disabled | **Yes — pending.** No results yet; re-capture after the checker merges (expected: 15/15 + 5/5 table with evidence) | A → redo in B |
| `04-feedback.png` | `/?tab=feedback` | Feedback memory: the 3 organizer-seeded records at the top (REC001 Accept / REC002 Edit / REC003 Reject with Chinese reasons + final actions), then 10 records written by smoke tests through the UI during the session (REC004–REC013, source `app`, reviewer `Duty manager`, `2026-10-24`), append-only table, counts 5 Accept / 8 Edit / 0 Reject | **No** (live `/api/feedback`; the extra rows are real test writes in `data/feedback.jsonl`, not mock data) | A |
| `05-about.png` | `/?tab=about` | About tab: what it does, data-quality notes DQ001–DQ004, the 12 operating rules table (RULE001–RULE005 visible) | **No** (static content from `/api/bootstrap`) | A |
| `06-assistant-result-interim.png` | `/?event=EVT001` (scrolled to risk card) | **Interim result page**: risk card `Medium · 中 · score 6.50`, detector card with 3 comparisons (SIGNAL −10.99 / no signal −3.66 / SIGNAL −9.14, `Unusual`), start of the fact sheet including `SIM-SCALE … is a Large airport` and **one** `ASSUMPTION` chip | **Partly** — analysis/UI is real; the checker panel further down still says "not checked" (no fake pass) | A (interim) |
| `07-assistant-result-tier-and-assumption.png` | `/?event=EVT001` (scrolled to fact sheet) | Fact sheet close-up: `SIM-BASE` facts, `SIM-SCALE … is a Large airport` (English tier — old bug showed 大型机场), **exactly one** `ASSUMPTION` chip, UNKNOWN gaps, forbidden actions, sources, prior feedback REC001 | **Partly** (display fix evidence; checker not involved) | A (interim) |
| `08-assistant-result-f07-chip.png` | `/?event=EVT001` (scrolled to 17 fields) | 17-field advice cards: `f03 Risk Level = Medium`, `f05 Evidence` with FACT·SIM-* chips incl. "Large airport", `f07 Assumptions to Verify` with **a single ASSUMPTION chip** (no duplicated `[ASSUMPTION]` text), `f08 Information Gaps`, `f09 First Action`, `f10 Follow-up` | **Partly** (f07/tier fix evidence; checker not involved) | A (interim) |
| `before/00-assistant-engine-fixtures.png` | `/` (old build) | **Before** evidence: old Assistant page with the wrong `engine: fixtures` badge | No (pre-fix state) | A (before) |

## `before/` — provenance

`before/00-assistant-engine-fixtures.png` is the pre-fix state captured by the Lead at
**16:25:13** and copied here from the workspace scratch file `scratch_shot.png`
(sha256 `FC3F1B24FB23D6A6B53BC77E70E2728AB4EC45D30F4E3481A309B3193B5C2F85`,
96 258 bytes, 1440×1000). It is the proof that the `engine:` badge used to read `engine: fixtures`.

Before/after story is now covered for **badge** (`before/…fixtures` → `01-assistant` `engine: real`),
**English tier** (`07`/`08` show "Large airport") and **single ASSUMPTION chip** (`07`/`08` show one chip).
There is no pre-fix image of the f07/tier bugs themselves (the UI was patched before the first
capture and the result page requires an analyze run) — do not invent one.

## Exact files

| File | Bytes | SHA-256 (first 12) | Captured |
|---|---|---|---|
| `01-assistant.png` | 95 991 | `434E5FECE7E7` | 16:35:16 |
| `02-detector.png` | 102 244 | `2B0AD626164C` | 16:35:17 |
| `03-exam.png` | 25 442 | `C91F423E36CA` | 16:35:18 |
| `04-feedback.png` | 92 540 | `D181DAD4DF9C` | 16:35:19 |
| `05-about.png` | 88 920 | `EFDD06ADEA1A` | 16:35:20 |
| `06-assistant-result-interim.png` | 102 344 | `3CEBD7B9E0C4` | 16:35:53 |
| `07-assistant-result-tier-and-assumption.png` | 83 330 | `C46A091E9493` | 16:35:55 |
| `08-assistant-result-f07-chip.png` | 110 517 | `CC727A417959` | 16:32:32 |
| `before/00-assistant-engine-fixtures.png` | 96 258 | `FC3F1B24FB23` | 16:25:13 (Lead) |

All 9 files were verified non-empty and visually checked: header badge `模拟 / SIMULATED` present
in every shot; 1440×1000; no broken layout.

## Pending (Phase B, after Lead says "checker green")

1. Re-capture `01`–`05` on the merged build (deterministic; keep the same URLs).
2. Add the **green checker** evidence: result page scrolled to the checker panel
   (`/?event=EVT001`), plus `06-bad-ai-demo.png` — checker panel **red** after the bad-AI demo,
   naming the invented number (live negative test).
3. `03-exam.png` — click **Run exam** so the results table (official x/15, own x/5,
   expected/forbidden/evidence columns) is visible. Without a real run this must stay "not checked".

Acceptance for Phase B: every image real and ≥ 1440×1000; no `engine: fixtures` in the badge;
result page shows exactly one ASSUMPTION chip and "Large airport"; the checker panel is either
genuinely green or honestly "not checked" — never a fabricated pass.

## How they were captured (reproducible)

Tooling lives in the workspace root, deliberately **not committed** (`_demo_capture.js` + JSON shot specs):

```powershell
# from the repo root, Lead's server already on :8811
node 'D:\下载\HackSHSID 2026\_demo_capture.js' 'D:\下载\HackSHSID 2026\_demo_capture_phaseA.json'   # 01-05
node 'D:\下载\HackSHSID 2026\_demo_capture.js' 'D:\下载\HackSHSID 2026\_demo_capture_result.json'   # 06-07
```

The harness launches headless Edge with `--remote-debugging-port`, drives it over CDP
(no extensions, no scrollbars, 1440×1000, deviceScaleFactor 1), waits for the app to boot /
for `?event=` analysis to render, optionally scrolls a card into view, and writes
`Page.captureScreenshot` PNGs. Plain `msedge --headless=new --screenshot=... --window-size=1440,1000`
works for the default tab only (no deep links or interaction).
