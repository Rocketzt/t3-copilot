# Repo update + self-check + fix plan — plain-language version

**Written 2026-10-24 · for the whole team · branch `jonathan`**
This is the human version. It says what changed, what we tested, what is still broken, and what we will do
about it in the simplest words I can manage. A short technical map is at the end for whoever does the edits.

---

## 1. The one-minute summary

**Good news**
- The whole repository was updated: all remote branches fetched, and `origin/main` was merged into `jonathan`
  without conflicts.
- The app itself works offline: 15/15 endpoint checks passed, JavaScript syntax is clean, and the detector
  reproduces the organizer numbers exactly (192 airport-months, 12 official flags, 13 any-signal, Hailing
  `-15.62 / -10.99`).
- Rebuilding `data/track3.json` from `Track 3 Data.xlsx` produces exactly the same file (no drift).
- 16/16 unit tests pass.
- The writer + real engine produce real-mode results, with exact risk labels (`Low` / `Medium` / `High` /
  `Can't tell`), no personal data, and no “weather caused” phrase.

**Bad news**
- The exam still reports **0/21**. That is **not** because 21 answers are bad: **20/21 cases meet every expected
  and forbidden text rule** and fail *only* because Ziyu’s checker is not merged. The last one, the “bad AI”
  test, needs that checker to block the fake number. In plain words: the report card says 0 because the
  examiner is missing, not because the student failed everything.
- We found a handful of real integration bugs that would show up as soon as the checker is merged, plus two
  visible UI bugs. They are listed in §4 and are all small.

**Next 3 things (in order)**
1. Review and merge **Ziyu’s checker** (`origin/ziyu`, commit `ed1b336`); it already exists — it is just not
   on `main` or on `jonathan`.
2. Make four small writer/pipeline fixes so normal outputs pass that checker.
3. Fix two visible UI bugs: the “Can’t tell” risk card and the mixed-language feedback table.

---

## 2. What changed in the repository

| Thing | State |
|---|---|
| `origin/main` | now `396598b` — includes Jason’s fact-sheet merge and a review note about Jonathan’s branch |
| `origin/jonathan` | now `c682fe5` (before this plan is committed) — our real-engine fixes |
| `origin/jason` | advanced to `322d6bb` (cross-check + D03 skeleton); **not merged** into this branch |
| `origin/ziyu` | `ed1b336` — **adds `engine/checker.py` (C01–C13) + `tests/test_checker.py`; not on `main` yet** |
| Local branch | `jonathan`; `origin/main` merged locally (`b0d74de`); working tree clean before this plan file |
| Data | `data/track3.json` rebuilds byte-for-byte the same from the workbook |

**What this means in plain words:** main has Jason’s engine, ziyu has the missing checker, and our branch has
the app + real-engine wiring. The next merge is obvious: get the checker from ziyu (after a quick review) onto
the branch we use for the exam.

---

## 3. What we ran (health check)

| # | Check | Command / method | Result |
|---|---|---|---|
| 1 | Unit tests | `python -m unittest discover -s tests` | **16/16 OK** |
| 2 | Exam | `python tests/run_tests.py --writer-mode offline` | **0/21 pass**, but 20/21 fail only `pipeline checker did not pass`; NEG001 fails `bad writer was not blocked` |
| 3 | HTTP endpoints | stdlib `urllib` script against `python app/server.py` | **15/15** (health, bootstrap, detector ranking/chart/airport, analyze EVT001/custom/bad, ask, feedback GET/POST, tests, checker demo, static, sheet06 404) |
| 4 | Detector truth | compare with `EXECUTION_PLAN` Appendix A | 192 rows; flags_own 12; flags_any 13; counts `{0:179,1:11,2:1,3:1}`; Hailing 2025-07 `-15.62 / -5.46 / -11.48`; Yunchuan 2025-07 YoY `-0.80` → **exact** |
| 5 | Writer/real engine | `pipeline.analyze` EVT001/003/005 | `engine_mode="real"`; risk `Medium` / `Can't tell` / `Low`; PII redacted; causal phrase absent |
| 6 | Data reproducibility | `python scripts/build_data.py` (build-time openpyxl) | same counts; `git diff data/track3.json` empty |
| 7 | Checker compatibility (read-only copy of ziyu checker, not merged) | `checker.check(output, facts)` on our outputs | EVT001–005 pass **after** two small writer fixes; OWN005 still fails C02 because custom IDs contain digits; bad output is correctly failed by the checker |
| 8 | JS syntax | `node --check app/static/app.js` | pass |
| 9 | Fixture vs real detector | normalise percentages and compare all 192 rows | **0 differences** (good now, but see B6 — two copies of the same data can drift later) |
| 10 | Build environment | `.venv` packages / pip | `.venv` has no third-party packages; PyPI is unreachable, so build scripts must use the machine’s bundled Python (already done) |

**Plain reading of the exam result:** the 15 official + 5 own cases satisfy their expected/forbidden patterns.
They are waiting for the checker. This is the right kind of “blocked”, not a content failure.

---

## 4. Bugs and fixes — plain language

Priority: **P0** = needed before the exam can be meaningful; **P1** = visible/consistency; **P2** = polish/docs.
“Owner” uses our normal split: J = Jonathan, Z = Ziyu, S = Jason.

| # | What is wrong (plain words) | Why it matters | Fix plan (plain words) | Owner | Time | Prio |
|---|---|---|---|---|---|---|
| **B1** | The exam has no checker, because Ziyu’s `engine/checker.py` is only on `origin/ziyu`, not on `main` or `jonathan`. | The exam cannot pass any case; the bad-AI demo cannot show a block. | Review Ziyu’s checker commit, merge it (or copy just `engine/checker.py` + its tests after review), then run the exam. No change to the checker logic. | Z + J | 30 min | **P0** |
| **B2** | Our writer adds detector “reason” lines to the Evidence field. Those lines contain numbers (e.g. “2 detector signals”) that are not in the fact-sheet number list, so the checker’s C02 would reject **every** output. | The exam would fail even with the checker merged. | Do **not** put derived reason lines in field f05. Keep f05 to the fact-sheet facts (they are already fully whitelisted). Risk reasons stay in the UI risk card only. | J | 20 min | **P0** |
| **B3** | The passenger draft says “check official airline and airport channels”. The checker wants the exact phrase “official channels” (C05). | Every output would be blocked on C05. | Change the default passenger wording to “Please check official channels for updates.” Keep it as a draft; no certainty words. | J | 5 min | **P0** |
| **B4** | Custom events use IDs like `TEST007` / `OWN005`. The checker masks `EVT…`, `RULE…`, `TEST…`, `REC…` but not `OWN…`, so the digits in the ID look like untraceable numbers (C02). | The custom/unseen-event exam cases would fail with the checker merged. | Two options, pick one at merge time: (a) teach the checker a generic ID mask, or (b) show custom events with a no-digit ID such as `CUSTOM` in the output. Prefer (a) if Ziyu agrees; (b) works without changing the checker. | Z + J | 20 min | **P0** |
| **B5** | In the UI, a `Can't tell` result is displayed as **“Medium”**, and the purple border style is lost (the CSS class gets a space in it). | Judges will click EVT003 and see the wrong risk label — exactly the case we use to show “we know when we can’t tell”. | Add `"can't tell": "Can't tell"` to the label map and normalise the class (`cant_tell`). Test by opening EVT003. | J | 10 min | **P1** |
| **B6** | The Detector tab, event cards and chart still use generated mock JSON (`fixtures/mock_*.json`), while analysis uses Jason’s real engine. Today they match exactly; tomorrow they can drift. | Two sources of truth: a number changed in one place would show differently on screen. | Switch `/api/bootstrap`, `/api/detector/ranking`, `/api/detector/chart`, `/api/detector/airport` to read the real modules when available, with the fixtures only as fallback. Add one equality test/cross-check. | J | 1–2 h | **P1** |
| **B7** | The Feedback tab mixes organizer seeds in Chinese (`接受/修改/拒绝`) with app records in English (`Accept/Edit/Reject`). | Looks sloppy in the demo and makes D05 harder to explain. | Use `engine.feedback.load_records()` (it already translates seeds) when available; fallback to the fixture only if needed. | J | 20 min | **P1** |
| **B8** | A typed-in event with no `id` shows `EVENT` as the Event ID, and a feedback record can be saved without a useful event id. | Feedback matching/recording gets weaker for typed events. | Give every typed event a stable no-digit ID (`CUSTOM`) before building the fact sheet; use it in output f01 and feedback. | J | 15 min | **P1** |
| **B9** | `/api/tests/run` returns the runner result without an `available` flag (the fallback has one). | Small contract inconsistency; UI works today but future code may read it. | Add `available: True` in the normal branch of `pipeline.run_tests`. | J | 5 min | **P2** |
| **B10** | The phrase cleaner turns “the weather caused it” into “the the monthly data shows…”. It also leaves the raw phrase in the echoed event text (the pipeline then scrubs it, but the grammar is ugly). | Cosmetic, but a judge reading the echoed input can see clumsy text. | Use a clean replacement such as “was associated with weather” and apply it once to both the output and the echoed event fields. | J | 10 min | **P2** |
| **B11** | The repository’s `.venv` has no `openpyxl` and pip cannot reach PyPI from this network. | `scripts/build_data.py` cannot run in the “official” venv, even though the app itself is fine. | Document clearly: the app needs only the standard library; `data/track3.json` is committed; to rebuild it, use the machine’s bundled Python that has openpyxl (or any offline environment). Add a note to README/D08. | J | 10 min | **P2** |
| **B12** | Docs are slightly stale: README says the checker is not available; `docs/project/LOG.md` has a review note saying the pipeline is not wired to the real engine. | Reviewers may read the old state and think less of the project. | After B1–B8, update README + log + D03/D05 numbers; add a one-paragraph “current state”. | S + J | 20 min | **P2** |
| **B13** | The 17 fields are English but event time/text fragments stay Chinese (organizer source). | Mixed language in a judge-facing output. | Optional: add a small English rendering for the five organizer events (the writer already has a place for it); leave custom user text as typed. | J | 30 min | **P2** |

---

## 5. Plan of record (do things in this order)

**Step 1 — get the examiner in (B1)**
- Ziyu reviews/merges `engine/checker.py` + `tests/test_checker.py` from `origin/ziyu` (or cherry-picks them).
- Run `python -m unittest tests.test_checker` and the compatibility probe; expect failures B2/B3/B4 only.

**Step 2 — make normal outputs checker-clean (B2, B3, B4)**
- Remove derived reason lines from f05.
- Change the passenger sentence to the checker’s expected “official channels”.
- Settle the custom-ID rule (generic mask in checker, or `CUSTOM` display id).
- Re-run the probe: EVT001–EVT005 must pass; the bad-AI output must fail; the hostile OWN005 must not leak PII.

**Step 3 — fix what the user sees (B5, B6, B7, B8)**
- Risk label + class; Detector tab/event cards switched to real modules; feedback seeds in English; typed-event IDs.
- Open the app in a browser: EVT003 must show **Can’t tell** in purple; Detector tab numbers must still match Appendix A; Feedback tab must show a single language; a typed event must get a clean ID.

**Step 4 — run the real exam (all three owners)**
- `python tests/run_tests.py --writer-mode offline`; expect **21/21 pass** if the checker and small fixes behave. If not, report the honest list — do **not** fake a pass.
- Update D03 (numbers from the real run), D05 (feedback record), D01 (risk/checker screenshots), and the log.

**Step 5 — polish and docs (B9–B13)**
- API `available` flag, cleaner phrase replacement, README/D08 note about the offline build, optional English event text.

---

## 6. How we will know it is fixed (acceptance)

- [ ] Unit tests: `python -m unittest discover -s tests` → all pass (currently 16/16).
- [ ] Exam: `python tests/run_tests.py --writer-mode offline` → 21/21, with NEG001 blocked; real output saved to `exports/test_results.json`.
- [ ] Checker probe: EVT001–EVT005 pass; hostile input has no PII; bad-AI output is blocked.
- [ ] HTTP: `/api/analyze` EVT003 f03 is exactly `Can't tell`; `/api/checker/demo` returns `blocked: true`; `/api/tests/run` has `available: true`.
- [ ] UI: EVT003 shows the purple Can’t-tell card; detector numbers unchanged; feedback tab is one language; typed event has `CUSTOM` id.
- [ ] Offline: app runs with no network and no API key; `模拟 / SIMULATED` visible everywhere.
- [ ] No source files changed by accident; data file untouched; no PII or “weather caused” in any output.

---

## 7. What we will NOT do

- We will not make the checker return “pass” when it is missing.
- We will not edit Jason’s detector/rules/facts or Ziyu’s checker logic unless the owner reviews it.
- We will not merge the whole `jason` or `ziyu` branches blindly; only the reviewed checker/test files needed for the exam.
- We will not rewrite history or push to `main`.

---

## 8. Technical map for the builder (short)

| File | Planned edit |
|---|---|
| `engine/pipeline.py` | (a) add `facts["detector"]`/`["rules"]` (already done); (b) assign `CUSTOM` id for typed events before `build_factsheet`; (c) use `engine.feedback.load_records/append_record` when present; (d) use real detector for `bootstrap/ranking/chart/airport` with fixture fallback; (e) `run_tests` add `available: True` |
| `engine/writer.py` | remove risk-reason lines from f05; passenger phrase “official channels”; cleaner phrase replacement; optional English time text |
| `app/static/app.js` | risk mapping `"can't tell": "Can't tell"` + class `cant_tell`; detector API adapter (real fields use fractions, UI expects `*_pct`); feedback display; custom ID |
| `app/server.py` | no structural change; `tests/run` shape comes from pipeline |
| `tests/` | add one integration test: analyze EVT001–005 → `checker.check` passes; bad output fails; custom ID passes C02 |
| `docs/` | README current state; D03/D05 numbers; this plan linked from log |

**Checker interface (from `origin/ziyu`):** `from engine.checker import check; check(output, facts) -> {"passed", "checks", "failures"}` — our pipeline already probes `check_output`/`check`/`validate`, so `check` will be used automatically.

---

## 9. Evidence appendix (for the curious)

- Branch tips at check time: `main=396598b`, `jason=322d6bb`, `ziyu=ed1b336`, `jonathan=c682fe5` (before this plan).
- `git merge origin/main` → clean, only `docs/project/LOG.md` added.
- `python -m unittest discover -s tests -v` → 16 tests OK.
- `python tests/run_tests.py --writer-mode offline` → 0/21; 20 failures are exactly `pipeline checker did not pass`; NEG001 is `bad writer was not blocked`.
- Checker probe (read-only copy of ziyu checker, not merged): after removing the f05 reason lines and using “official channels”, EVT001–EVT005 pass; OWN005 fails C02 because `OWN005` is not masked; bad output fails (as it must).
- HTTP: 15/15 endpoints passed; custom hostile event had no `张伟`/`13812345678` and no “weather caused”.
- Data rebuild: `scripts/build_data.py` produced the same `data/track3.json` (no git diff).
- Fixture vs real detector: 0 differences across 192 rows after normalising percentages (so the current UI numbers are correct today).
