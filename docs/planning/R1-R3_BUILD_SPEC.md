# R1–R3 build specification (for an AI coding agent)

**Scope:** add three small features to the existing T3 Ops Copilot plan — **R1 source receipts**, **R2 ask-the-assistant
question chips**, **R3 "what changed?" re-analysis** — without changing the detector, the 17-field format, the checker
policy, the exam expectations, or the offline demo.
**Audience:** an AI coding agent (Claude Code / Codex / Cursor) operating on the `t3-copilot` repository.
**Repo state assumed:** commit `05b52fd` — planning documents + folder skeleton, **no Python/JS code yet**. Read
`EXECUTION_PLAN.md`, `CONTRACT.md`, `docs/planning/ERRATA.md`, `README.md` first. Where this spec and the repo
disagree, this spec wins for R1–R3 only; the repo wins for everything else.

---

## 0. How to use this file

1. Read §1–§3. Run the **precondition check** (§2). Do not start coding before it passes.
2. Build one **slice** at a time: Slice A = R1, Slice B = R2, Slice C = R3. Each slice is shippable alone.
3. After every task (T-number): run its test, update the repo's work-log convention, commit with the message given.
4. Stop at the end of a slice if time runs out. **Never leave `main` broken.**
5. Use §12 (master prompt) if the agent needs a single starting instruction.

**Timeboxes** (AI-agent estimates; a human pair will be comparable): R1 ≈ 1.5 h, R2 ≈ 2 h, R3 ≈ 2.5 h, full
integration ≈ 1 h. If the build is running late, ship R1 only; R2 next; R3 last.

---

## 1. Product context the agent must internalise

The app is a local, offline, Python-stdlib + vanilla-JS web app for airline staff. Five tabs: **Assistant**,
**Detector**, **Exam**, **Feedback**, **About**. A user picks an organizer event (EVT001–EVT005) or types a new one.
The pipeline is:

```
event → data/detector (3 comparisons) → fact sheet (facts, sources, assumptions, unknowns, risk)
      → rules engine (RULE001–012) → writer (template offline | LLM optional | bad mode)
      → checker (blocks invented numbers, committed actions, PII, causal claims, missing 模拟)
      → 17-field output + 3 message drafts → human Accept/Edit/Reject → append-only feedback log
```

Hard rules that R1–R3 must not break:

1. **Code owns facts.** Every number the assistant says must have a source ID; the checker verifies it.
2. **Offline first.** Runtime = Python 3.10+ standard library only. No CDN, no fonts, no npm, no network calls in
   the default mode. Data comes from `data/track3.json` (built once by `scripts/build_data.py`).
3. **模拟 / SIMULATED** appears in every page and every generated output.
4. **No PII** in inputs, outputs, logs. Redact phone/ID/email.
5. **The assistant never decides.** Decisions on cancellation/release/dispatch/maintenance/compensation appear only
   as items a human must decide (field f12).
6. **Read-only organizer file.** `Track 3 Data.xlsx` is never modified.
7. **Additive API changes only.** Existing JSON keys/fields must keep working.

**The three features, in one line each:**
- **R1** — every number/fact in the fact sheet carries a clickable "receipt" (sheet, row, columns, formula, period).
- **R2** — the Assistant page has a bounded "Ask the assistant" panel: the official test questions as chips + a
  free-text box, answered by the **same** `pipeline.ask()` the exam uses; answers carry checker status and sources.
- **R3** — after an answer, staff can add new information for the **same event** and re-analyse; the app shows
  old→new risk/actions with the reason, while the original runs stay in an append-only run history.

---

## 2. Precondition check (stop/go)

Run these checks before writing feature code. If a check fails, follow the stop rule.

| # | Check | Command / signal | If missing |
|---|---|---|---|
| P1 | `data/track3.json` exists and has 192 baseline rows, 12 rules, 15 tests, 5 events, 3 feedback seeds | `python scripts/build_data.py`, then inspect counts | Build it first (EXECUTION_PLAN Z1) — R1–R3 depend on it |
| P2 | `engine/pipeline.py` exposes `analyze(event, writer_mode=...) -> dict` and `ask(question, event, writer_mode=...) -> dict` (or the CONTRACT §6 equivalents) | import and call | If absent: build **UI components against fixtures** (T2 fixtures) and mark backend tasks blocked. Do not rebuild the whole engine as part of R1–R3 |
| P3 | `app/server.py` serves static files and `/api/analyze`; `app/static/{index.html,app.js,styles.css}` exist | `python app/server.py` → `http://127.0.0.1:8803` | Same as P2 |
| P4 | Detector numbers match Appendix A of EXECUTION_PLAN (12 flags, 13 any-signal, Hailing 07/08, Yunchuan −0.80) | `python tests/runner.py --writer-mode offline` or the detector's validation print | **STOP.** Fix data/detector first; never build UI on wrong numbers |
| P5 | `docs/planning/ERRATA.md` read; the corrected missing-weather rows are used (**Qinglan 2025-03, Gaoyuan 2025-09, Hailing 2025-11, Linjiang 2025-11**) | grep | Fix before R1 receipts quote weather origins |

**Stop rule:** on P2/P3 failure, ship only the fixture-driven UI (T2, T9–T11) and leave the backend slice blocked;
report exactly which interface is missing. On P4 failure, stop all work and report.

---

## 3. Shared contracts and conventions

### 3.1 Files the agent may modify

```
engine/facts.py            (add origin objects; no behaviour change to numbers)
engine/checker.py          (allow the new human-update source; no policy relaxation)
engine/pipeline.py         (accept optional update/previous_run_id; return run_id + change)
engine/qa.py               (if absent, create: intent router for R2)
engine/run_history.py      (new: append/read run records)
engine/change.py           (new: diff previous vs current)
app/server.py              (add/extend endpoints; keep existing routes)
app/static/index.html      (R1 popover, R2 ask card, R3 update/diff cards)
app/static/app.js          (R1/R2/R3 behaviour)
app/static/styles.css      (popover/cards)
fixtures/                  (new JSON fixtures for UI-first work)
tests/                     (new unittest files + a verify script)
docs/                      (only a short note; do not rewrite deliverables)
```
Do not modify: `Track 3 Data.xlsx`, `EXECUTION_PLAN.md`, `CONTRACT.md`, `docs/planning/ERRATA.md`, deliverable
drafts owned by others, or any detector formula.

### 3.2 Source registry (additive)

Existing source IDs: `SIM-BASE`, `SIM-SCALE`, `SIM-WEATHER`, `RULE001`–`RULE012`, `EVT001`–`EVT005`, plus virtual
`DETECTOR`, `FEEDBACK-HISTORY`, `EVENT`. **Add `HUMAN-UPDATE`** (staff-provided information for the current event).
The checker's source validator must accept it; it must still reject any other unknown source.

### 3.3 JSON conventions

- All text files UTF-8; `ensure_ascii=False`.
- Every timestamp ISO-8601 with offset, e.g. `2026-10-24T10:31:00+08:00`.
- `run_id` format: `YYYYMMDDTHHMMSS-<EVENT_ID>`; collisions get `-2`, `-3`.
- Numbers compared with tolerance 0.02 pp (the workbook has ±0.01 rounding).
- PII scrub before storing any user text (phone `1[3-9]\d{9}`, ID `\d{17}[\dXx]`, email).

### 3.4 UI conventions

- Vanilla JS, one `app.js`, no modules/deps. Event delegation via `data-*` attributes.
- Cards: `.card`, `.card-title`, `.badge`, `.chip`, `.btn`, `.btn-ghost`, `.empty`, `.error-banner`, `.loading`.
- Every generated text area shows `模拟 / SIMULATED`.
- Keyboard: popovers close on `Esc`; buttons are real `<button>` elements; focus returns to the trigger.
- Loading state on every network action; friendly error banner; never a blank page.

---

## 4. R1 — Source receipts

### 4.1 Goal
Any number or fact the user sees can be clicked to reveal where it came from: source ID, workbook sheet, row,
columns, formula, period, time scale — or, for rules/events/feedback, the rule row / event row / record.

### 4.2 Data contract (fact sheet addition)

Every item in `facts[]` **and** every item in `numbers[]` gains an `origin` object:

```jsonc
{
  "kind": "data",                  // "data" | "rule" | "event" | "derived" | "feedback" | "human_update"
  "source": "SIM-BASE",            // must match the item's source
  "sheet": "01_机场月度运行基线",   // null for derived/human
  "row": "2025-07 海陵国际机场",    // human-readable; required for data/rule/event/feedback
  "row_index": 176,                // optional, 1-based sheet row if known
  "columns": ["E", "H", "I"],      // optional
  "formula": "I = (E - H) x 100; column I is already in percentage points",
  "period": "2025-07",             // month, event window, or rule table
  "time_scale": "monthly"          // "monthly" | "event_window" | "rule" | "past_decision" | "human_input"
}
```

Origin rules by source:

| source | sheet | row | formula example | time_scale |
|---|---|---|---|---|
| `SIM-BASE` | `01_机场月度运行基线` | `2025-07 海陵国际机场` | `I = (E-H)x100 (already pp); G = same-class mean of E` | monthly |
| `SIM-SCALE` | `02_机场年度规模` | `2025 海陵国际机场` | `annual passengers / movements` | monthly (annual row) |
| `SIM-WEATHER` | `03_机场天气月度` | `2025-08 海陵国际机场` | `monthly weather background` | monthly |
| `DETECTOR` | `null` | `2025-08 海陵国际机场` | `own=I; peer=(E-G)x100; yoy=E(2025,m)-E(2024,m)` | monthly |
| `RULE0xx` | `05_运营规则` | `RULE003` | `trigger: delta_pp <= -5.00` | rule |
| `EVT00x` | `04_模拟事件` | `EVT001` | `verbatim event text (organizer)` | event_window |
| `FEEDBACK-HISTORY` | `07_人工反馈` | `REC003 / EVT005` | `append-only record` | past_decision |
| `HUMAN-UPDATE` | `null` | `user input <timestamp>` | `verbatim staff update; PII removed` | human_input |

**Guardrails:**
- Never fabricate `sheet`/`row`; derive them from `data/track3.json` row objects (which already carry year/month/airport).
- `origin.source` must equal the fact's `source`; a test enforces this.
- Payload size is acceptable; do not strip origins for the API (the UI needs them).
- The checker does **not** scan `origin` text for numbers (it only scans output text), so formulas like `x100` are safe.

### 4.3 API
No new endpoint. `POST /api/analyze` response gains `origin` inside `facts[]` and `numbers[]`.
Add to `GET /api/bootstrap` a static `receipt_sources` map (optional, for About): source → description.

### 4.4 UI behaviour (Assistant page, fact sheet panel)

- Each fact row already shows a value/source chip. Make the chip a `<button class="receipt-trigger" data-receipt='<json>'>`
  (embed the origin JSON, HTML-escaped) or use `data-fact-id` + a JS lookup map built from the analyze response.
- Preferred: `data-fact-id="F07"`; `app.js` keeps `window.__lastAnalyze.facts` indexed by id; click → `openReceipt(origin)`.
- Also make the source IDs in field **f16 Cited Sources** clickable → show a source summary card: description,
  which facts/rows used, period(s).
- Popover content (title + definition list):
  ```
  Where this comes from
  Value:      -15.62 pp
  Source:     SIM-BASE
  Sheet:      01_机场月度运行基线
  Row:        2025-07 海陵国际机场
  Columns:    E, H, I
  Formula:    I = (E - H) x 100 (already percentage points)
  Period:     2025-07 (monthly data)
  Footer:     模拟 / SIMULATED — organizer-generated data
  ```
- Empty origin (should never happen) → show "No receipt available — this is a bug, do not trust this number."
- Mobile: popover becomes a bottom sheet; one instance at a time.

### 4.5 Tests
`tests/test_r1_receipts.py` (stdlib `unittest`):
1. build fact sheets for EVT001, EVT003, EVT005;
2. every `facts[]` and `numbers[]` item has `origin` with required keys;
3. `origin.source == item.source`; `sheet` in the allowed set for the source kind; `row` non-empty;
4. the `-15.62 pp` fact's origin is sheet 01, row containing `2025-07` and `海陵国际机场`;
5. every origin `sheet`/`row` exists in `data/track3.json` (match by year/month/airport);
6. a deliberately broken fact (origin removed) makes the test fail.

### 4.6 Acceptance
- Clicking a fact value shows the receipt with correct sheet/row/formula.
- Clicking a source in f16 shows the source summary.
- No receipt exists for a fabricated number (the checker blocks it before the UI).
- Works offline, no console errors.

---

## 5. R2 — Ask-the-assistant panel

### 5.1 Goal
On the Assistant page, the user can ask a question about the **current event**. Answers come from the same
`pipeline.ask()` used by the exam, are fact-grounded, carry checker status and sources, and refuse unsafe requests.
It is **not** a free chatbot: a bounded intent router answers common questions; anything else returns a bounded
"what we can say + gaps" answer.

### 5.2 Backend contract
`POST /api/ask`
```jsonc
// request
{
  "question": "Will flights definitely be delayed?",   // 3..500 chars, required
  "event_id": "EVT001",                                // one of event_id | custom
  "custom": null,                                      // same schema as /api/analyze custom
  "writer_mode": "offline"                             // auto|offline|live; default auto
}
// response
{
  "question": "...",
  "event_id": "EVT001",
  "intent": "delay_certainty",
  "answer": {
    "text": "No. A risk is not a confirmed delay. ... [FACT: SIM-BASE] ... 模拟 / SIMULATED",
    "mode": "offline",
    "sources": ["SIM-BASE", "SIM-WEATHER", "RULE002"]
  },
  "check": {"passed": true, "checks": [{"id": "A01", "name": "numbers traceable", "status": "pass", "detail": ""}]},
  "event_context": {"airport": "海陵国际机场", "risk_level": "Medium", "month_label": "2025-08"}
}
```
Errors: `400` empty/too-long question; `404` unknown event; `500` with `{error, detail}`; never echo PII.

### 5.3 Intent router (`engine/qa.py`)
Order matters — first match wins. Match on lowercased text, Chinese and English. Each intent has: `intent`, `keywords`,
`required_tags`, `must_avoid`, `answer_builder(fact_sheet, output) -> text`, `sources`.

| # | intent | example triggers (EN + ZH) | answer must (checked) | must avoid |
|---|---|---|---|---|
| 1 | `pii` | phone/ID/email pattern in question | refuse to use it; redact; advise deleting | repeating the PII |
| 2 | `auto_action` | "automatically cancel", "just cancel", "send now", "自动取消", "直接发送" | refuse; name responsible role (Operations Lead / relevant professional); no simulated action | 已取消/已发送/"has been cancelled" |
| 3 | `simulation` | "real airport?", "is this real", "真实的吗" | explain all data/events are simulated (DQ001); 模拟 | claiming real |
| 4 | `conflict` | "which source", "two sources", "冲突", "不一致" | cannot choose; verify update time/definition; can't tell | picking a source |
| 5 | `causality` | "did weather cause", "because of weather", "天气导致" | association only; monthly data cannot prove cause | causal claim |
| 6 | `delay_certainty` | "will it be delayed", "definitely", "一定", "延误" | separate risk from formal status; no certainty | "will be delayed" |
| 7 | `why_risk` | "why risk", "why Hailing", "为什么" | cite the three comparisons with numbers + weather + importance | unsourced numbers |
| 8 | `missing_info` | "aircraft position", "which flights", "前序飞机", "具体航班" | list gaps from `missing_data`/`unknowns`; no invention | invented position |
| 9 | `rejection` | "reject", "overrule", "拒绝", "否决" | explain append-only record, original kept, next advice adjusts | overwriting human opinion |
| 10 | `downgrade` | "resources sufficient", "wind within limits", "资源充足" | re-assess; explain what changed | clinging to old risk |
| 11 | `time_range` | "which period", "which month", "时段", "哪个月" | event window vs monthly baseline 2024-01…2025-12; no mixing | mixing single month/cumulative |
| 12 | `stop` | "source reliability unknown", "can't tell", "可靠性" | stop conclusions; list gaps; named escalation | continuing firm advice |
| 13 | `two_messages` | "write to ops and passengers", "分别写" | return the two existing drafts (different) | identical text |
| 14 | `new_airport` | "new airport", "Linjiang", "临江" | answer for the event's actual airport; if question names another, say to use New event | canned Hailing answer |
| 15 | `fallback` | anything else | "The event data cannot answer that. What we can say: risk X; first action Y; gaps Z." + sources | invented facts |

**Answer text rules:** every clause tagged `[FACT: <source>]` / `[ASSUMPTION]` / `[UNKNOWN]` / `[HUMAN]`; end with
`模拟 / SIMULATED`; 3–8 sentences; no markdown tables; no PII. Keep a short deterministic sentence bank so the
offline mode needs no LLM. The LLM may be used only if configured; the checker still runs.

### 5.4 `pipeline.ask()` requirements
- Build (or reuse) the fact sheet once for the event; pass it to qa and checker.
- `checker.check_answer(answer_text, fact_sheet)` checks: numbers traceable, sources valid, no committed actions,
  no PII, 模拟 present, no causal claim. Return the same check-item shape as output checks.
- Answer sources = union of sources used by the fact sheet facts quoted.
- Cache fact sheet per event per process to keep latency < 1 s.

### 5.5 UI (Assistant page, below the 17 fields)
```
┌ Ask about this event ─────────────────────────────────────────────┐
│ [Definitely delayed?] [Why is risk up?] [Which source?] ... chips │
│ [ free-text input .......................................] [Ask]  │
│ ── answer card ─────────────────────────────────────────────────  │
│ intent badge · mode badge (offline/live) · checker ✓/✗            │
│ answer text with source chips · [copy]                            │
└───────────────────────────────────────────────────────────────────┘
```
- Chips are generated from `GET /api/bootstrap` → add `tests[]` (id, type, question_zh, question_en, label).
  Send the **English** question text to `/api/ask` (the router supports both; keep one canonical text per chip).
- Include a "New airport demo" chip? No — TEST007 is covered by the New event form/Exam tab. Do not add a chip that
  silently changes the event.
- Keep last 5 Q&A in the DOM; no persistence. `Esc`/clear button resets. Disable Ask while loading.
- Show an explicit hint: "Bounded question panel — not a general chatbot. Answers are grounded in this event's facts."

### 5.6 Tests
`tests/test_r2_ask.py`:
1. for each of the 15 official tests: call `ask(en_question)` and `ask(zh_question)`; assert `check.passed` and the
   expected/forbidden patterns from `tests/cases_official.py` (reuse; do not fork);
2. `pii`: answer does not contain the phone/ID; mentions redaction;
3. `auto_action`: refuses and names a role; no 已取消/已发送;
4. `conflict`: EVT003 answer contains "can't tell"/"无法判断" and verification action;
5. `fallback`: gibberish question returns sources and no invented numbers;
6. latency < 2 s offline; no network access.
`scripts/verify_r1_r3.py` also hits `/api/ask` once over HTTP.

### 5.7 Acceptance
- All 15 chips answer with checker ✓ and a mode badge.
- A judge-typed question gets a grounded answer or a bounded fallback — never a blank or an invented fact.
- Hostile inputs are refused in the product, not just in the exam.

---

## 6. R3 — "What changed?" re-analysis

### 6.1 Goal
For the **same event**, staff add new information (e.g. "resources confirmed sufficient"), click Re-analyse, and see
`old → new` risk/first action/escalation with the reason, while the previous run stays available and immutable.
This is *not* feedback memory: feedback memory records accept/edit/reject after a decision and affects **future
similar events**; R3 applies new information to **this** event immediately.

### 6.2 Run history (new)
`data/run_history.jsonl` — append-only, one JSON per analysis:

```jsonc
{
  "run_id": "20261024T101500-EVT005",
  "created_at": "2026-10-24T10:15:00+08:00",
  "event_id": "EVT005",
  "event_input_hash": "<sha256 of normalised inputs>",
  "previous_run_id": null,
  "update_intent": null,
  "mode": "offline",
  "checker_passed": true,
  "risk_level": "Medium",
  "risk_score": 2.5,
  "output_fields": { "f03": "...", "f09": "...", "f11": "...", "f16": "..." },   // at least these
  "detector": {"signal_count": 1, "verdict": "watch", "month_label": "2025-02"},
  "sources": ["SIM-BASE", "..."]
}
```
Helpers in `engine/run_history.py`: `append(record) -> record`, `load(run_id) -> record | None`,
`list_for_event(event_id, limit=10) -> list[summary]`, `verify_append_only() -> bool` (file only grows).
Do **not** store full fact sheets/outputs if size becomes a problem; the four fields + detector summary are enough
for the diff. PII is scrubbed before append. `GET /api/runs?event_id=EVT005` returns summaries (no PII).

### 6.3 Update input and intent parsing (`engine/change.py`)
`POST /api/analyze` request gains:
```jsonc
{
  "event_id": "EVT005",
  "writer_mode": "offline",
  "previous_run_id": "20261024T101500-EVT005",   // optional; required for a diff
  "update": { "text": "Ground-support resources confirmed sufficient; wind within limits." }  // optional
}
```
`update.text` max 500 chars. Parse into one intent (first match):
| intent | triggers (EN + ZH) | effect on risk | first action template |
|---|---|---|---|
| `downgrade` | resources sufficient, capacity confirmed, wind within limits, 资源充足, 保障能力已确认, 风速可控, 人员充足 | one level lower (min Low) | "Record the confirmed resource position and continue monitoring; re-check if the weather worsens." |
| `escalate` | runway closed, flight cancelled, formal delay notice, mass delay, 跑道关闭, 正式延误通知, 大面积延误, 机场关闭 | one level higher (max High) | "Confirm the scope with the Operations Lead; do not take operational action." |
| `resolve_conflict` | source reviewed, both definitions consistent, 已复核, 统计口径一致 | if Can't tell → Watch/Medium | "Confirm which source was reviewed and that both use the same definition; then re-assess." |
| `note` (default) | anything else | unchanged | unchanged |

Effects are **bounded and explicit**: append a `HUMAN-UPDATE` fact (text verbatim after PII scrub), add factor
"human update: <intent>", run the writer/checker again, and never add an operational action. If the update is empty
or unparsable → `note`. If no `previous_run_id` → normal analyse (no diff). Invalid id → `404`/`400` with a clear
message.

### 6.4 Diff object (added to the response)
```jsonc
{
  "run_id": "20261024T103000-EVT005",
  "change": {
    "previous_run_id": "20261024T101500-EVT005",
    "summary": "Risk lowered from Medium to Low after staff-confirmed resource information; no operational action taken.",
    "changed": [
      {"key": "f03", "label": "Risk Level 风险等级", "from": "Medium", "to": "Low",
       "reason": "HUMAN-UPDATE (downgrade): resources confirmed sufficient → risk lowered one level; RULE006/RULE007 still block automatic action."},
      {"key": "f09", "label": "First Action 第一步行动", "from": "Ask the airport coordination team ...",
       "to": "Record the confirmed resource position and continue monitoring; re-check if the weather worsens."}
    ],
    "update_applied": {
      "intent": "downgrade",
      "text": "Ground-support resources confirmed sufficient; wind within limits.",
      "facts_added": [{"id": "F21", "text": "...", "source": "HUMAN-UPDATE"}]
    },
    "previous": {"run_id": "...", "risk_level": "Medium", "first_action": "..."}
  }
}
```
If nothing material changes: `change.summary = "No material change; the update was recorded."`, `changed: []`.
Comparison keys (minimum): `f03`, `f09`, `f11`, detector `signal_count`/`month_label`, `sources` (added/removed).
The previous run is never modified; `previous_run_id` links backwards.

### 6.5 UI (Assistant page)
- **Update card** (under the risk card, above the 17 fields): textarea + example chips
  ("Resources confirmed sufficient", "Formal delay notice issued", "Source A reviewed") + `Re-analyze` button.
- On response with `change`:
  - **Diff card** at the top: `Previous run (10:15) → Current (10:30)`; rows `Risk: Medium → Low`, `First action: … → …`;
    "Why: human update (downgrade)"; warning that decisions remain human.
  - Buttons: **View previous advice** (read-only modal/collapse), **Keep current** (dismiss diff, keep result).
- If `changed: []`: neutral card "No material change; update recorded."
- If error: keep current output, show banner, do not lose text.
- `模拟` visible; no auto-refresh; no persistence beyond the run history.

### 6.6 Tests
`tests/test_r3_change.py`:
1. analyse EVT005 → record run; `previous_run_id` present in response; `data/run_history.jsonl` grew by 1;
2. re-analyse with `update.text = "Ground-support resources confirmed sufficient; wind within limits."` →
   `change.changed` includes `f03` Medium→Low and `f09` change; `summary` mentions human update; previous run still
   loadable and unchanged;
3. escalate update → risk rises (max High) and first action points to Operations Lead; no committed action text;
4. unrelated update → `changed: []`, summary "No material change";
5. invalid `previous_run_id` → 404; empty update → 400; PII in update → redacted before storage;
6. run history is append-only (line count never decreases); two runs have distinct ids.
`scripts/verify_r1_r3.py` repeats 2 and 4 over HTTP.

### 6.7 Acceptance
- A judge sees risk/flip + reason + old advice preserved.
- No change is invented; bounded intents only.
- Works offline; previous run immutable.

---

## 7. Task list (build in this order)

| # | Slice | Task | Files | Acceptance |
|---|---|---|---|---|
| T1 | all | Recon: read `EXECUTION_PLAN.md`, `CONTRACT.md`, `ERRATA.md`, `data/track3.json`; run preconditions P1–P5; write `docs/planning/R1-R3_NOTES.md` with the exact interfaces found/missing | notes | notes exist; stop/go decision recorded |
| T2 | all | Create fixtures for UI-first work: `fixtures/analyze_EVT001_origins.json`, `fixtures/analyze_diff_EVT005.json`, `fixtures/ask_answers.json` (15 official questions, event-specific answers) | fixtures/ | JSON parses; shapes match §4.2/§5.2/§6.4 |
| T3 | R1 | Add `origin` to `facts[]`/`numbers[]` in `engine/facts.py` for data/scale/weather/detector/rule/event/feedback; add `HUMAN-UPDATE` placeholder origin helper | engine/facts.py | import works; EVT001 fact sheet prints origins |
| T4 | R1 | Allow `HUMAN-UPDATE` in checker source registry; no other policy change | engine/checker.py | checker still blocks unknown sources; EVT001 unchanged |
| T5 | R1 | Tests `tests/test_r1_receipts.py` per §4.5 | tests/ | pass |
| T6 | R1 | UI popover: `index.html` template, `app.js` `openReceipt/renderReceipt/wireReceipts`, `styles.css`; attach to fact values + f16 sources | app/static/* | click works offline; Esc closes; no console errors |
| T7 | R2 | `engine/qa.py` intent router + answer builders (offline deterministic); bilingual; `pipeline.ask` returns answer+check; add `tests[]` to bootstrap | engine/qa.py, engine/pipeline.py, app/server.py | ask returns grounded answer; checker passes |
| T8 | R2 | `POST /api/ask` route with validation, PII scrub, 400/404/500, latency <2 s | app/server.py | curl works |
| T9 | R2 | Tests `tests/test_r2_ask.py` + reuse official cases | tests/ | 15/15 ask-checker pass |
| T10 | R2 | UI ask card: chips (from bootstrap), free text, answer card (mode/check badges/sources), loading/error | app/static/* | 15 chips answer; hostile inputs refuse |
| T11 | R3 | `engine/run_history.py` (append/load/list) + hook in `pipeline.analyze` (always save; return `run_id`) | engine/run_history.py, engine/pipeline.py | run file grows; ids unique |
| T12 | R3 | `engine/change.py`: update intent parser, bounded risk/first-action effects, diff builder | engine/change.py, engine/facts.py | 4 intents behave per §6.3 |
| T13 | R3 | `/api/analyze` accepts `previous_run_id` + `update`; returns `change`; validation | app/server.py, engine/pipeline.py | HTTP tests from §6.6 pass |
| T14 | R3 | Tests `tests/test_r3_change.py` | tests/ | pass |
| T15 | R3 | UI update + diff card; previous advice modal; no-change state | app/static/* | demo scenario works offline |
| T16 | all | Wire fixtures → real API (remove mock branch); keep a `?fixtures=1` dev switch if useful | app/static/app.js | real data renders; fixtures not required |
| T17 | all | Integration script `scripts/verify_r1_r3.py` (pipeline + HTTP smoke), README section, screenshots | scripts/, README | script exits 0 |
| T18 | all | Regression: `python tests/runner.py --writer-mode offline`; detector numbers unchanged; EVT001/003/005 behaviours unchanged; offline test | tests | no regressions |
| T19 | all | Commit per slice; update `docs/project/log/<name>.md` (or the repo's convention); notify the team | docs/project | clean `git status` except intended files |

**Commit messages:** `feat(receipts): add origin receipts to fact sheet and UI` · `feat(ask): add bounded ask panel and API` ·
`feat(change): add re-analysis diff and run history` · `test(r1-r3): ...` · `docs(r1-r3): ...`.

---

## 8. Test plan

**Automated (stdlib `unittest`, run from repo root):**
```bash
python -m unittest tests.test_r1_receipts -v
python -m unittest tests.test_r2_ask -v
python -m unittest tests.test_r3_change -v
python scripts/verify_r1_r3.py
python tests/runner.py --writer-mode offline     # regression, 15 official + 5 own + negative
```
**Manual UI checklist (screenshots for evidence):**
1. Assistant → EVT001 → click `-15.62 pp` → receipt shows sheet 01 / 2025-07 Hailing / E,H,I / formula.
2. Click a source in f16 → source summary lists the rows used.
3. Ask chips: `Definitely delayed?` → answer separates risk/status; checker ✓.
4. Ask `Automatically cancel all flights` → refusal names a responsible role; no `已取消`.
5. Ask a question containing a phone number → PII refused/redacted.
6. Ask gibberish → bounded fallback with gaps, no invented number.
7. EVT005 → add "resources confirmed sufficient" → re-analyse → diff Medium→Low, first action changes.
8. "View previous advice" still shows the old output.
9. Add a neutral note → "No material change" (no invented diff).
10. Restart app → run history still lists both runs; no PII in `data/run_history.jsonl`.
11. Offline (network disabled): all of the above works.
12. Regression: Detector tab numbers unchanged; Exam tab still runs.

**Do not ship if:** a test fails and time has run out; instead revert the slice and ship the previous green commit.

---

## 9. Integration and scheduling constraints

- R1–R3 must be built as **one branch** (`feature/r1-r3`), merged to `main` only when its slice's tests pass.
- They are **additive**: no change to detector maths, no change to the 17-field list, no change to existing API keys.
- Recommended slots (per EXECUTION_PLAN): **do not start before G2 (Sat 15:30)**. If G2 is green with ≥60 min spare,
  build R1 in 15:30–16:30 while docs continue. R2 only if G2 is green before ~14:30. R3 only if both are green and
  the docs/rehearsal are not at risk. Feature freeze 21:00 is absolute.
- If no slack: implement the fixtures + tests and **document R1–R3 as future work** in D06/D07 (do not half-merge UI).
- Anyone can revert a slice by reverting its commits; slices do not depend on each other except R2/R3 need the
  fact sheet and `pipeline.ask/analyze` that already exist in the core plan.

---

## 10. Guardrails (the agent must not)

- invent a number, sheet, row or formula; if data is missing, show "no receipt available" and expose a failing test;
- add third-party runtime dependencies, CDNs, web fonts, or network calls in offline mode;
- change detector thresholds, the 17-field list, the checker's existing checks, or the exam cases;
- write to `Track 3 Data.xlsx` or commit `.env`/keys;
- store PII in `run_history.jsonl`, logs, fixtures or commits;
- use Chinese text in console output (Windows garbles it) — write UTF-8 files and read them;
- make the UI look like an open chatbot; R2 is a bounded question panel;
- let R3 change risk silently: every change needs a reason, an intent, and the previous run preserved;
- claim a feature works without running its test.

---

## 11. Definition of done

- [ ] All R1/R2/R3 tests pass; `scripts/verify_r1_r3.py` exits 0; regression suite unchanged.
- [ ] `python app/server.py` on a clean checkout (with `data/track3.json`) renders all three features offline.
- [ ] Every fact/number has an origin; every ask answer has checker status and sources; every re-analysis has a
      reason and preserves the previous run.
- [ ] `HUMAN-UPDATE` accepted by the checker; unknown sources still rejected.
- [ ] No PII in outputs, logs, run history, fixtures.
- [ ] README updated with the three features, commands and the bounded-question note.
- [ ] Commit history is per-slice and the branch merges cleanly.

---

## 12. Master prompt for the coding agent (paste this first)

> You are working in the `t3-copilot` repository for HackSHSID 2026 Track 3, commit `05b52fd`. Read `README.md`,
> `EXECUTION_PLAN.md`, `CONTRACT.md`, `docs/planning/ERRATA.md`, and `docs/planning/R1-R3_BUILD_SPEC.md` in full
> before writing code.
>
> Your job: implement R1 (source receipts), R2 (bounded ask-the-assistant panel), R3 (what-changed re-analysis) exactly
> as specified in `R1-R3_BUILD_SPEC.md`. This is additive work: do not change the detector, the 17-field list, the
> checker's existing checks, the exam cases, the offline-first stack, or the organizer workbook. Python stdlib only at
> runtime; vanilla JS; no CDNs; all text UTF-8; every output keeps `模拟 / SIMULATED`.
>
> Work slice by slice (R1 → R2 → R3), task by task (T1–T19), and after each task: run its test, commit with the
> specified message, and update the work log. If a precondition in §2 fails, stop and report exactly which interface
> is missing — do not rebuild the whole engine. If you cannot finish a slice, leave `main` green and document the
> remaining work; never half-merge.
>
> The most important invariants: (1) every number the assistant says is traceable to the fact sheet and the checker
> enforces it; (2) R2 is a bounded question panel, not an open chatbot; (3) R3's risk changes are bounded, reasoned
> and never overwrite the previous run; (4) the app works offline with no network.

---

### Appendix — minimal JSON examples

**Fact with origin (R1):**
```json
{"id": "F07", "text": "Hailing 2025-07 completion 69.49% vs own 12-month average 85.11% (-15.62 pp).",
 "value": -15.62, "unit": "pp", "source": "SIM-BASE",
 "origin": {"kind": "data", "source": "SIM-BASE", "sheet": "01_机场月度运行基线",
            "row": "2025-07 海陵国际机场", "columns": ["E", "H", "I"],
            "formula": "I = (E - H) x 100; column I is already in percentage points",
            "period": "2025-07", "time_scale": "monthly"}}
```

**Ask response (R2):**
```json
{"question": "Will flights definitely be delayed?", "event_id": "EVT001", "intent": "delay_certainty",
 "answer": {"text": "No. A risk is not a confirmed delay; no formal flight status was provided. The simulated weather notice shows heavy rain and gusts over the next 6 hours [FACT: EVT001], and Hailing's 2025-08 completion was 73.16% versus its own average of 84.15% (-10.99 pp) [FACT: SIM-BASE]. 模拟 / SIMULATED", "mode": "offline", "sources": ["EVT001", "SIM-BASE"]},
 "check": {"passed": true, "checks": []},
 "event_context": {"airport": "海陵国际机场", "risk_level": "Medium", "month_label": "2025-08"}}
```

**Re-analysis diff (R3):**
```json
{"run_id": "20261024T103000-EVT005",
 "change": {"previous_run_id": "20261024T101500-EVT005",
  "summary": "Risk lowered from Medium to Low after staff-confirmed resource information; no operational action taken.",
  "changed": [
    {"key": "f03", "label": "Risk Level 风险等级", "from": "Medium", "to": "Low",
     "reason": "HUMAN-UPDATE (downgrade): resources confirmed sufficient → risk lowered one level."},
    {"key": "f09", "label": "First Action 第一步行动", "from": "Ask the airport ...", "to": "Record the confirmed resource position and continue monitoring."}],
  "update_applied": {"intent": "downgrade", "text": "resources confirmed sufficient", "facts_added": [{"id": "F21", "text": "...", "source": "HUMAN-UPDATE"}]},
  "previous": {"run_id": "20261024T101500-EVT005", "risk_level": "Medium", "first_action": "Ask the airport ..."}}}
```
