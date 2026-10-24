# D01 — Five-minute client presentation outline

> 模拟 / SIMULATED — fictional airports, events and numbers from the organizer workbook. The screenshots linked below are real captures of the app; several are interim captures taken before checker integration.

**Owner:** Jason · **Status:** Eleven-slide outline with speaker notes, following `EXECUTION_PLAN.md` §9.1. Jonathan drives the live app; Jason narrates the opening, exam and limits; Ziyu explains detector and checker. All numeric claims below were checked against the current detector, `exports/test_results.json`, and the bad-writer demo.

### Slide 1 — Our airline’s disruption desk (0:00–0:25, Jason)

**On screen:** “An operations assistant for our airline’s disruption desk.” 模拟 / SIMULATED.
**Speaker note:** We are one fictional airline. Our duty staff need to decide which of *our* airports to review first, what to verify and which messages to prepare. The assistant drafts; qualified people decide.
**Visual:** [01-assistant.png](../evidence/screenshots/01-assistant.png) — real default app page.

### Slide 2 — Type a new event (0:25–0:50, Jonathan)

**On screen:** Our event form: Hailing, 14:00, heavy rain and gusts in the next six hours, busy afternoon.
**Speaker note:** Enter the event live and choose Analyze. We are not selecting a canned answer. The screenshot proves the form exists; the live click proves this input path.
**Visual:** [01-assistant.png](../evidence/screenshots/01-assistant.png) — form before entry.

### Slide 3 — Risk with its time context (0:50–1:15, Jonathan)

**On screen:** Risk card, detector context, source badges and the 17-field output after the live analysis.
**Speaker note:** Read the risk shown by the live run, then point to the selected month and missing information. The saved image shows an EVT001 example with risk Medium; it is illustrative, not a capture of the new event typed on stage.
**Visual:** [06-assistant-result-interim.png](../evidence/screenshots/06-assistant-result-interim.png) — earlier EVT001 result; checker status in this capture is interim.

### Slide 4 — Facts before prose (1:15–1:40, Jonathan)

**On screen:** SIM-BASE, SIM-SCALE and SIM-WEATHER sources; assumptions and unknowns in separate places.
**Speaker note:** Scroll from the evidence to information gaps and first action. The fact sheet identifies its sources and prevents a monthly pattern from becoming a claim about one flight.
**Visual:** [07-assistant-result-tier-and-assumption.png](../evidence/screenshots/07-assistant-result-tier-and-assumption.png) — real fact-sheet close-up.

### Slide 5 — Three audiences, human decisions (1:40–2:00, Jonathan)

**On screen:** f13 for our operations staff; f14 for airport coordination; f15 as a passenger draft. f12 lists the decisions reserved for people.
**Speaker note:** Open the three message tabs live. We ask the airport partner to confirm capacity; we do not order it. A person reviews any passenger draft before release.
**Visual:** [08-assistant-result-f07-chip.png](../evidence/screenshots/08-assistant-result-f07-chip.png) — real 17-field cards; use the live app for the message tabs.

### Slide 6 — Network triage (2:00–2:25, Ziyu)

**On screen:** **12 own-history flags → 2 multi-signal months → 1 first priority** in the simulated network.
**Speaker note:** Open Detector. The engine checks the airport’s own history, same-size peers and the same month last year. We rank signals first, then importance to our airline. Hailing is first in the current network view.
**Visual:** [02-detector.png](../evidence/screenshots/02-detector.png) — real detector chart and ranking.

### Slide 7 — Why Hailing leads (2:25–2:45, Ziyu)

**On screen:** Hailing 2025-07: own **−15.62 pp**, peer **−5.46 pp**, YoY **−11.48 pp**. Yunchuan 2025-07 YoY: **−0.80 pp**.
**Speaker note:** Hailing crosses the signal threshold on all three comparisons in that month. Yunchuan’s July YoY gap does not. These are monthly airport comparisons, not flight outcomes.
**Visual:** [02-detector.png](../evidence/screenshots/02-detector.png) — highlight the July ranking and comparison chart.

### Slide 8 — Show the invented-number gate (2:45–3:20, Ziyu)

**On screen:** Live bad-AI demo: fabricated **“20 points”** in f05; checker C02 blocks it.
**Speaker note:** Click the bad-AI demo and read the displayed C02 failure. The current engine call returns `blocked: true` and names the unwhitelisted number. No committed operational action follows a blocked draft.
**Visual:** Live checker panel. No post-integration checker screenshot is in `evidence/screenshots/`; do not present an interim screenshot as a green checker result.

### Slide 9 — Feedback changes the review path (3:20–3:55, Jonathan)

**On screen:** EVT005 organizer Reject; Gaoyuan first action: `confirm current resources`.
**Speaker note:** Open feedback, then re-analyze Gaoyuan. The earlier rejection is retained; the advice asks staff to verify current resources. The screenshot contains additional smoke-test records, so identify the organizer seed rather than treating all rows as airline staff feedback.
**Visual:** [04-feedback.png](../evidence/screenshots/04-feedback.png) — real feedback table; live app for the re-analysis.

### Slide 10 — What the exam proves (3:55–4:30, Jason)

**On screen:** Fresh offline exam **21/21**: 15 official, five own, one negative. TEST003 checks “Can’t tell”; TEST005 refusal; TEST011 privacy.
**Speaker note:** Run the Exam tab live and show the result table. The saved `03-exam.png` is the initial tab before a run; the fresh CLI output is `exports/test_results.json`. This is automated must/must-not and checker evidence, not a human tone score.
**Visual:** [03-exam.png](../evidence/screenshots/03-exam.png) — initial state only; live result table after the click.

### Slide 11 — Value, limits and next gate (4:30–5:00, Jason)

**On screen:** Our desk narrows **12 flags to 1 first review**; source-backed drafts and human decisions. Next: shadow mode, assisted use, monitored use.
**Speaker note:** We have shown a simulated priority, a blocked fabricated number and the exam. Monthly data cannot identify a flight or prove weather caused an outcome. We would need real airline feeds and reviewer sign-off before operational use. Invite questions.
**Visual:** [02-detector.png](../evidence/screenshots/02-detector.png) for the priority story; D06 and D07 provide the risk and rollout details.

## Demo control and fallback

Keep the `模拟 / SIMULATED` badge visible. Jonathan should pre-open the app and test the Analyze, bad-AI, feedback and Exam clicks. `evidence/demo_recording_plan.md` is a recording plan, not evidence that a finished video exists; use a recording only after it is captured and checked. Never claim the interim screenshots show a checker pass or a completed exam.

## What we did not build

No live flight, crew or gate feeds; no flight-level causal model; no automatic cancellation, dispatch or official passenger sending; no measured real-airline outcome improvement. The talk shows the working simulated prototype and its test limits.
