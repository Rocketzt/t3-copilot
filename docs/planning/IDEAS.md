# Ideas that fit the current repo — inventory + additions

**Planning note, not a submission deliverable.** Written against the repo state at commit `05b52fd`
(`EXECUTION_PLAN.md`, `CONTRACT.md`, `docs/planning/ERRATA.md`, five-tab plan, no code yet).

**Why the previous ideas felt random:** they were written before this repo existed, as *extra research
methods* (black box, pre-registration, FMEA, difference-in-differences). They were not tied to your five
tabs and they competed with a 30-person-hour build that has very little slack. Ignore that list for now.
This file has one rule:

> **An idea only belongs here if it (1) strengthens a part you already planned, (2) makes a judge question
> easier to answer, (3) costs ≤ 1 hour, (4) uses existing data/pipeline, and (5) can be dropped without
> touching the core.** Otherwise it goes in D06/D07 as "future work", not into the build.

---

## 1. What you already have (in the plan — not built yet)

### 1.1 Engine — the four parts

| Part | What is already planned | Why it scores |
|---|---|---|
| **Part 2 · Detector** | 3 comparisons (own 12-month average · same-size peers · same month last year), 0–3 signals, verdict normal/watch/unusual/clearly unusual, confidence, ranking of 192 airport-months, Hailing-vs-Yunchuan chart, independent cross-check | Answers "how do you define a disruption?" and "which one is serious?" with numbers |
| **Part 1a · Fact sheet + rules** | Facts with source IDs, assumptions, unknowns, missing data, forbidden actions, deterministic risk score (EVT001 Medium, EVT003 Can't tell, EVT005 feedback-downgraded), RULE001–012 → checks/action/escalation/manual approval | Answers "can every assessment be traced? facts vs assumptions vs unknowns?" |
| **Part 1b · Writer + checker** | Offline template writer (default) or optional LLM (OpenAI-compatible); 17 fields + 3 drafts; tags `[FACT: src]`/`[ASSUMPTION]`/`[UNKNOWN]`/`[HUMAN]`; checker blocks invented numbers, bad sources, committed actions, PII, causal claims, missing 模拟; fail → retry → fallback; **bad mode** for the live negative test | Answers "isn't this just ChatGPT?" — code owns the facts |
| **Part 4 · Feedback memory** | Append-only JSONL, organizer seeds (accept EVT001 / edit EVT004 / reject EVT005), match by airport then rule, quote prior decision, original preserved | Answers "what happens when staff reject the advice?" |
| **Part 3 · Exam** | 15 official tests + 5 own events + 2 adversarial + 1 fabricated-number negative test; expected vs forbidden; evidence; run-1 vs run-2; report + filled sheet 08 | Answers "does it handle unseen events, and how do you know?" |

### 1.2 UI — the five tabs (from EXECUTION_PLAN §3.2)

| Tab | Already planned on it |
|---|---|
| **Assistant** | Event picker (EVT001–005) + new-event form → risk card, detector card, fact sheet (facts/assumptions/unknowns/missing), 17-field grid with Chinese labels + source chips, 3 message tabs with copy, checker panel (red = feature), Accept/Edit/Reject bar |
| **Detector** | Stat cards (192 months · 12 official flags · 13 any-signal · 1 three-signal), sortable ranking, inline SVG Hailing-vs-Yunchuan chart with peer line and Jul/Aug highlight, cross-check note |
| **Exam** | Run button, official x/15 + own x/5 summary, results table (expected / forbidden / evidence), report download |
| **Feedback** | Append-only log, accept/edit/reject counts, original advice vs human edit side by side |
| **About** | What it is, 4 parts, 12-rules reference, DQ001–004 notes, counts, limitations, 模拟 note |

### 1.3 Evidence / delivery

- D01–D08 drafts exist as stubs; D03 gets `filled_sheet08.xlsx`; extra `filled_sheet06.xlsx` (5 events × 17 fields).
- `NUMBERS.md` as the single number source; `exports/` for test results, cross-check report, chart PNG.
- AI-use log (`docs/AI_USAGE.md`) and the three AI jobs (AI-C cross-check, AI-R citations, AI-D doc drafts).
- Modes: `offline` default, `live` optional, `bad` for the checker demo. `模拟` everywhere.

**So you already have more nuance than most high-school teams:** three comparisons instead of the official one, a
checker that can block the AI, conflict/missing-data handling, append-only feedback, and a 22-case exam. The ideas
below are about making that nuance **visible and testable in the app** — not adding new parts.

---

## 2. Recommended additions (pick 1–3, max)

### R1 · Source receipts — click any number, see where it came from · 45–60 min
- **Where:** Assistant result page, on every number and every `[FACT: SIM-BASE]` chip.
- **What:** a small popover: value · source ID · sheet name · row (e.g. sheet 01, 2025-08 Hailing) · formula/time range.
  For rules, show the rule row (trigger/action).
- **Why it exists:** the brief's main question is "can every key assessment be traced to data or rules?" Today the
  chips show an ID; the receipt shows the actual cell. A judge can verify in one click.
- **Implementation:** Ziyu adds `origin: {sheet, row, formula, period}` to fact/number objects in the fact sheet
  (~20 min). Jonathan adds one popover component and attaches it to the existing chips (~40 min). No new data.
- **Demo line:** "Click 73.16% — sheet 01, 2025-08 Hailing, column E; column I says −10.99 pp and is already in
  percentage points."
- **Done when:** every numeric badge opens a receipt; no receipt ever shows an invented origin.

### R2 · "Ask the assistant" question chips · 60–90 min
- **Where:** Assistant result page (below the 17 fields) — a small card with the 15 official questions as buttons
  plus a free-text box.
- **What:** clicking a chip calls the existing `pipeline.ask(question, event)` and shows the answer + checker status
  + sources. It is **not an open chatbot**: answerable questions get grounded answers; hostile/unanswerable ones get
  the refusal/gap answer the exam already tests.
- **Why it exists:** the brief is written as questions ("will flights be delayed?", "which source?", "can you send
  it?"). Today those only exist in the Exam tab; putting them in the product lets a judge test one live without
  leaving the main screen. It also makes Part 3 visible as a feature, not just a report.
- **Implementation:** Jonathan adds `/api/ask` wiring + chips UI (~60 min); Ziyu already needs `ask()` for the
  runner, so no new engine work beyond returning `answer + check + sources` (already in CONTRACT §6).
- **Demo line:** "Judge, pick a question. 'Will flights definitely be delayed?' — it separates risk from formal
  status, cites the baseline, and the checker confirms no invented number."
- **Done when:** all 15 chips return answers with checker status; PII/cancel requests are refused.

### R3 · "What changed?" panel — re-analyze after new information · 60–75 min
- **Where:** Assistant result page; a "New information" box + "Re-analyze" button; diff card next to the risk card.
- **What:** staff add/confirm one fact (e.g. "ground-support resources confirmed sufficient") and re-run. The app
  shows **old → new**: risk level (Medium → Low), first action (confirm capacity → monitor), and the reason
  (new fact `[HUMAN]`), while the original advice stays visible.
- **Why it exists:** the brief explicitly asks how the assistant adapts when information changes or a person
  rejects the advice; TEST013 covers it, but today a judge only sees the final answer. A diff makes adaptation
  visible in five seconds, and it doubles as the EVT005 feedback story.
- **Implementation:** Ziyu: `analyze(..., update=...)` merges the new fact and returns `previous` vs `current`
  (~30 min). Jonathan: two-column diff card (~30 min). Store the previous run in the browser session; no database.
- **Demo line:** "Add 'resources confirmed sufficient' → risk drops, the first action becomes monitoring, and the
  original advice is still on screen."
- **Done when:** diff shows old/new risk + ≥1 changed action + reason; original output still retrievable.

**If you only add one:** R1 (receipts). It directly answers the judges' #1 question and is the smallest change.
**If you add two:** R1 + R2. **R3** only if G2 (15:30) is green early.

---

## 3. Optional additions — only if G2 passes early (each ≤ 1 h)

| # | Idea | Tab/part | Why it exists (judge question) | Effort | Risk |
|---|---|---|---|---|---|
| O1 | **Devil's-advocate panel** — 2–3 automatic "why this might be wrong" bullets (Yunchuan also dipped; no formal status; weather row missing; importance small) | Assistant | "Under what circumstances would it fail?" — shows the assistant argues against itself | 45 min | Low (template text) |
| O2 | **Compare two airports** — pick A and B; side-by-side 3 comparisons + 12-month lines | Detector | "Why Hailing and not Yunchuan?" becomes interactive | 1–1.5 h | Medium (new UI) |
| O3 | **Similar events panel** — list past events at the same airport / same fired rule, with organizer feedback outcome | Assistant / Feedback | "What happens when staff reject?" visible *before* deciding | 45–60 min | Low |
| O4 | **Checklist mode** — first actions become tick-boxes; "verified" saved with the feedback record | Assistant → Feedback | Human role is enforced, not just described (D05 evidence) | 45 min | Low |
| O5 | **Message quality meter** — passenger draft: character/SMS count, highlighted certainty words, required "official channels", audience checklist | Assistant | "Are the 3 messages right for each audience?" made checkable | 45 min | Low |
| O6 | **History / replay** — every analysis saved with timestamp; click to reload | Assistant | Traceability + demo recovery (a simple version of the "black box" idea) | 60–90 min | Medium |
| O7 | **Month picker** — choose the evidence month for the detector instead of assuming the latest flagged month | Assistant form | Fixes the "which month did you use?" assumption (ERRATA C9) and lets a judge test any month | 45 min | Low |
| O8 | **Printable duty-manager card** — print view: risk, 3 checks, escalation, 3 drafts, sources | Assistant | Tangible artifact for the demo/Q&A | 30–45 min | Very low |
| O9 | **Seasonal context line** — under the detector: "Yunchuan also dropped ~6 pp in July; network July 78.8% vs March 84.3% → that part is normal" | Detector | Pre-empts "isn't a summer dip normal?" | 30 min | Very low |
| O10 | **Required sign-offs panel** — which roles must approve (RULE007/RULE008) | Assistant | "Who decides?" governance clarity | 30 min | Very low |

---

## 4. Free additions — no UI work, do these anyway (≈ 30 min total)

1. **In the writer template**, add two bullets to field f07 (Assumptions to Verify):
   "Yunchuan and other airports also dip in July, so the seasonal part is not unusual" and
   "no formal operating status was confirmed at input time". (Template text, 15 min.)
2. **In field f10 (Follow-up Actions)**, add: "If capacity is confirmed sufficient → downgrade and monitor;
   if a formal irregularity appears → escalate to the Operations Lead." Already implied by the rules; writing it
   explicitly makes the "what would change the advice" idea free. (15 min.)
3. **In D03**, add a small "what we expected before running vs what happened" table (predictions written tonight,
   results filled Saturday). No code; makes the test report look mature. (20 min writing.)
4. **In D04/D06**, add one line each: "we considered a fourth statistical comparison (difference-in-differences);
   it confirmed the ranking but we did not add it, to avoid double-counting seasonality." (10 min writing.)

---

## 5. Ignore these from the earlier list (and why)

| Earlier idea | Why it is not worth build time now |
|---|---|
| Hash-chained "black box" | A plain History/replay (O6) gives the demo value for 1/3 of the work; the hash chain is a nice story but not a rubric requirement |
| Pre-registration document | Free version = the expected-vs-actual table in D03 (§4.3); no separate feature needed |
| Red-team mutation suite (50 mutations) | Genuinely good, but it is exam/evidence work; if time exists, let Jason add it to D03 as an extra table, not code |
| FMEA risk card (S×O×D) | One optional table in D06; do not build UI for it |
| Difference-in-differences, z-scores, sensitivity ribbon | Appendix paragraphs in D04/D03 at most; the detector already has three comparisons and a cross-check |
| Trust label ("Traceable 100% · 14/14 checks") | Cheap (30 min) but R1 receipts already carry the traceability story; skip unless everything else is green |
| Comprehension test with 5 people | Nice D03 extra if people are around; not a build task |
| Aviation-safety-culture framing | Story only; if the team likes it, use it in D01 words, not code |

**Rule:** every one of these goes into D06/D07 "future work" unless the core build is finished early.

---

## 6. How this fits Saturday (names, times, drop order)

The plan has ~30 person-hours of work in ~36–40 productive hours. **Do not start any addition before G2
(15:30)**; a missed G2 costs more than any idea here is worth.

| Time | Action |
|---|---|
| Tonight (23:15–01:15) | No additions. G0 first (data JSON + detector + app boot). |
| Sat 09:00–15:30 | Core build. At G2, ask: "did we pass with ≥ 60 min spare before 16:00?" |
| **If yes (G2 green + spare)** | **One** addition only: R1 receipts (Ziyu + Jonathan, 60 min) in the 15:30–16:30 window, while Jason starts D03/D04; then continue docs. |
| **If G2 green and very early (before 14:30)** | Add R2 ask chips as the second item; still freeze features by 21:00. |
| **If G2 is late or barely green** | Zero code additions. Use the free additions in §4 (template text + D03/D04 paragraphs) and put R1–R3 in D06/D07 "future work" + D01 "what's next". |
| Sat 16:00–21:00 | Docs, screenshots, rehearsal, submission — additions never push into this. |

**Owners:** R1/R2/R3 engine side = Ziyu; UI side = Jonathan; evidence/D03/D06/D07 text = Jason.
**Drop order if anything slips:** R3 → R2 → R1 → free additions. Never cut core test fixes, the checker demo,
17 fields, 3 messages, D01–D08, or the 模拟 labels.

---

## 7. Bottom line

- You do **not** need a "creative layer". Your plan already contains the differentiators: three comparisons, a
  checker, conflict/missing-data handling, feedback memory, a 22-case exam.
- The best "creative" move for high-school judges is to make those differentiators **visible**: a receipt under
  every number, a question they can ask live, a before/after when information changes. That is R1–R3.
- Everything else is documentation or future work. Feature count does not score; coherence does.
