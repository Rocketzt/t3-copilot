# D04 — Data and rules explanation

> 模拟 / SIMULATED — all airports, events and numbers are fictional (organizer data).

**Owner:** Ziyu · **Status:** Complete — written 2026-10-24. Every number below came from running
the code that day: `engine.detector`, `engine.network`, `engine.pipeline` and
`python tests/run_tests.py --writer-mode offline` (21/21). Nothing is quoted from memory.

We are the operations assistant for **one fictional airline's disruption desk**. This document
explains to our own staff and to reviewers where every number we show comes from, and which
rules the assistant applies before it drafts anything.

## 1. The data we use (all simulated)

One organizer workbook (`Track 3 Data.xlsx`, 14 sheets), exported once to `data/track3.json`;
rebuilding the export reproduces the file exactly.

| Sheet | What we take from it | Rows |
|---|---|---:|
| 01 Monthly operating baseline | completion, release, own 12-month average, peer average, gap column | 192 |
| 02 Airports & airline business | size tier and **importance to our airline** (高/中/低) | 8 |
| 03 Monthly weather | precipitation, max wind, bad-weather days, missing-data flag | 192 |
| 04 Events (EVT001–EVT005) | time window, weather/ops text, importance, known/unknown | 5 |
| 05 Rules (RULE001–012) | triggers, checks, actions, escalation, forbidden actions | 12 |
| 07 Human feedback | 3 seed records (Accept / Edit / Reject + reason) | 3 |
| 08 Tests (TEST001–TEST015) | official acceptance questions | 15 |
| 09–12 | the 17 output fields, source list, data-quality notes, checklist | — |

- **8 airports × 24 months = 192 airport-months** (2024-01 → 2025-12).
- **Column I (与自身平均差) is already in percentage points.** We never multiply it by 100.
- **Four weather rows are marked missing** (values exist in the sheet but must not be used):
  Qinglan 2025-03, Gaoyuan 2025-09, Linjiang 2025-11, Hailing 2025-11. We never impute them;
  confidence drops and the output must say so (checker C10).
- Data sources are `SIM-BASE`, `SIM-SCALE`, `SIM-WEATHER`; rules are `RULE001–012`; events are
  `EVT001–005`. `REF-CAAC` / `REF-CMA` are reference-only and may never back a claim.

## 2. What counts as a disruption (our definition)

Three comparisons per airport-month; each fires a **signal** when it is **≤ −5.0 pp**:

1. **Own history** — completion vs the airport's own 12-month average (column I, already pp).
2. **Same-size peers** — completion minus the same-class average.
3. **Same month last year** — 2025 month vs the same 2024 month (2024 rows have no YoY).

| Signals | Verdict |
|---:|---|
| 0 | normal |
| 1 | watch |
| 2 | unusual |
| 3 | clearly unusual |

With fewer than 2 comparisons available the verdict is **"can't tell"** (never happens in this
24-month dataset; the rule is still in the code). **Confidence** = 1 − 0.15 × (3 − comparisons
available) − 0.1 × (weather missing).

Across the whole network today: **192 airport-months, 12 own-history flags, 13 airport-months
with ≥ 1 signal**, signal counts **179 / 11 / 1 / 1** — only **2** months are multi-signal.

**Worked example — Hailing International Airport 2025-07** (the planted anomaly):

| Comparison | Value | Signal |
|---|---:|---|
| Own history: 69.49% vs own average 85.11% | −15.62 pp | yes |
| Same-size peers | −5.46 pp | yes |
| Same month last year | −11.48 pp | yes |

3 signals → **clearly unusual**, confidence 1.0. Hailing 2025-08 follows at −10.99 / −3.66 /
−9.14 pp → 2 signals, **unusual**.

**The contrast — Yunchuan 2025-07:** own history −6.07 pp (a flag) but peers **+5.47 pp** and
YoY **−0.80 pp** → 1 signal, *watch*. Its July dip is **seasonal**, not a disruption: the
network's mean completion is 78.80% in July and 78.51% in August against 84.29% in March. We do
not escalate a seasonal dip. (Beiling 2025-12 is the opposite edge: it flags on **YoY alone**,
own −4.74 / peer −3.86 / YoY −5.59 pp → 1 signal, watch.)

## 3. Network priority — which of *our* airports first

`engine.network.network_view()` sorts our 8 airports by **anomaly × importance to our airline**
(signals first, then 高/中/低 importance, then the own-history gap), each airport shown against
its latest anomalous month:

| # | Airport | Importance to us | Month | Signals | Verdict | Own pp |
|---:|---|---|---|---:|---|---:|
| 1 | Hailing International | High | 2025-08 | 2 | unusual | −10.99 |
| 2 | Yunchuan International | High | 2025-08 | 1 | watch | −5.94 |
| 3 | Beiling | Medium | 2025-12 | 1 | watch | −4.74 |
| 4 | Qinglan | Low | 2025-08 | 1 | watch | −6.49 |
| 5 | Gaoyuan | Low | 2025-02 | 1 | watch | −6.10 |
| 6 | Linjiang | Low | 2025-08 | 1 | watch | −5.44 |
| 7 | Nanwan | Medium | 2025-12 | 0 | normal | −0.13 |
| 8 | Xinghu | Medium | 2025-12 | 0 | normal | +2.23 |

**12 flags → 2 multi-signal → 1 priority review.** Hailing is the airport our desk looks at
first; Yunchuan, equally important to us, stays on watch because its dip is seasonal.

## 4. The 12 rules as our code fires them (`engine/rules.py`)

All triggers are deterministic keyword/signal checks — no LLM decides whether a rule fires.

| Rule | Fires in our code when | Action | Escalate to | Manual approval | Forbidden |
|---|---|---|---|---|---|
| RULE001 Insufficient info | source-conflict words, or ≥ 2 unknown items about source/definition/update time | soften the judgement, list the gaps | operations lead | yes | no firm conclusions |
| RULE002 Weather risk | medium/strong weather words **and** no formal operating status yet | prepare monitoring list + communication drafts | ops coordination | yes | must not claim flights will definitely be delayed |
| RULE003 Anomaly | **own-history signal only** (see deviation note) | flag for focused review | ops analyst | no | no direct weather attribution |
| RULE004 Sustained pressure | pressure keywords in the ops text (drop, backlog, congestion…) | ordered verification checklist | operations lead | yes | must not adjust real flight plans |
| RULE005 Passenger comms | same condition as RULE002 | produce a draft explicitly marked 草案 | passenger-service lead | yes | must not auto-send as official notice |
| RULE006 Human overrule | prior feedback matched, or reject/overrule words in notes | adjust advice to the new facts, keep the original record | model owner | yes | never overwrite human input |
| RULE007 Major decisions | **decision words only** (取消/放行/调度/维修/赔付, cancel/release/dispatch/maintenance/compensation) | stop advising; list the human decisions and required info | specialist owners | yes | no automated decision |
| RULE008 High-risk escalation | ≥ 2 independent risk signals (multi-signal context, weather risk, pressure, conflict) | recommend escalation with the trigger basis | operations lead | yes | no skipping human approval |
| RULE009 Citations | always (output contains numbers/status) | list sources in the output | output reviewer | yes | no unsourced facts |
| RULE010 Simulation label | always | label 模拟 everywhere | project owner | no | must not present it as a real event |
| RULE011 Privacy | PII patterns in the input (mobile, ID, email, 姓名/手机) | redact; use aggregates only | data owner | yes | never store sensitive personal data |
| RULE012 Stop condition | conflict, safety keywords, or verdict "can't tell" | stop action conclusions; output gaps + human escalation | operations lead | yes | no continued firm advice |

**Two documented deviations** (ERRATA C7/C8, recorded in `docs/planning/ERRATA.md`):
- **RULE003 fires on the own-history signal only** — the organizer rule is "5 pp below its own
  12-month average", not any-signal. (Beiling 2025-12 still appears in the ranking via its YoY
  signal, but RULE003 itself does not fire for it.)
- **RULE007 fires only on the decision words**, not on "risk level Medium+". Listing the human
  decisions every time is still our default behaviour, by design.

## 5. Facts, assumptions and unknowns — kept separate by construction

`engine/facts.py` builds a **fact sheet** before any prose is written:

- every **fact** has an id (F01…) and a source id; every usable **number** goes on a whitelist
  (`facts.numbers`) with value, unit, display text and source;
- **assumptions** are tagged `[ASSUMPTION]` (e.g. monthly patterns may indicate risk but do not
  prove a current flight impact);
- **unknowns** come from the event's own unknown list (per-flight plans, aircraft rotation, crew
  and ground-support status) and are never silently filled;
- **missing data** is listed separately and never imputed.

The writer — template or LLM — may only turn whitelisted facts into prose. It never computes a
number.

## 6. The checker (C01–C13): the gate the writer cannot argue with

`engine/checker.py` runs 13 deterministic checks on every output; a failure names the offending
text, one retry is allowed, then a deterministic fallback marked *needs human review*:

| | Check | | Check |
|---|---|---|---|
| C01 | all 17 fields present and non-empty | C08 | 模拟 present in f13/f14/f15/f17 |
| C02 | every number within 0.01 of a whitelisted value | C09 | source conflict ⇒ risk shown as Can't tell |
| C03 | `[FACT: X]` tags cite real fact-sheet sources | C10 | missing weather data is disclosed |
| C04 | no committed-action wording (已取消/已发送…) | C11 | prior feedback mentioned when it exists |
| C05 | passenger text is a draft, points to official channels, asserts no delay | C12 | no unhedged weather-causation claim |
| C06 | ops/airport/passenger messages pairwise distinct | C13 | f12 lists all five human-decision categories |
| C07 | no PII (mobile numbers, ID numbers, emails) | | |

Evidence from today's runs: the offline exam passes **21/21** (15 official + 5 own + 1 negative),
and the deliberately bad writer is blocked with *"unwhitelisted number 20 in field f05"*.

## 7. The 17-field output (mapping)

Every answer is the organizer's fixed 17-field shape: f01 Event ID · f02 Generated At ·
f03 Risk Level · f04 Airport & Time Window · f05 Evidence · f06 Possible Impact ·
f07 Assumptions to Verify · f08 Information Gaps · f09 First Action · f10 Follow-up Actions ·
f11 Escalation Conditions · f12 Decisions Requiring a Human · f13 Internal Ops Note ·
f14 Airport Coordination Message · f15 Passenger Message Draft · f16 Cited Sources ·
f17 Output Status. Audience split: **f13 goes to our own staff; f14 to the airport coordination
team (a partner we ask, not order); f15 is a draft a person reviews; f12 holds the five
human-only decisions** (cancellation, release, dispatch, maintenance, compensation).

## 8. Limits

- **Monthly, airport-level, simulated data.** We can say a month was unusual; we cannot attribute
  any single flight's delay, and we never claim to (C12 blocks unhedged causation).
- No live feeds: the context month is the latest anomalous month, labelled as such.
- Decisions stay with qualified people; the assistant only prepares information.

## What we did not build

No flight-level data, schedules, crew pairings or gate positions (the organizer data has none
and we never invent them); no live airport status feeds; no real CAAC/CMA figures (reference-only
sources are never cited as data); no automated decisions of any kind; no Excel exports of
organizer sheets 06/08 (cut from scope to fit the hours); the optional live-LLM writer mode is a
demo path only — the default writer is the deterministic template.
