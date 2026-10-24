# Language switch (EN / 中文) — analysis and implementation plan

**Status:** design ready, not implemented. **Owner:** Jonathan (web app). **Base:** branch `jonathan` at `f6f1ea2`.
**Scope:** `app/static/` only, plus one whitelist line in `app/server.py`. No engine, checker, exam or data changes.

---

## 1. What exists today (measured, not estimated)

| File | Size | Notes |
|---|---|---|
| `app/static/index.html` | 297 lines | 67 static visible text nodes, all English; tabs are `Assistant / Detector / Exam / Feedback / About` |
| `app/static/app.js` | 814 lines | ~305 quoted literals (UI copy + markup), 5 tabs rendered from `state` payloads |
| `app/static/styles.css` | 357 lines | has an existing `.zh` class for muted Chinese sub-labels |
| `app/server.py` | 226 lines | 12 JSON endpoints + a **static-file whitelist** (`STATIC_FILES`, lines 24–29) |
| `engine/i18n.py` | 14 lines | `AIRPORT_EN` (8 airports), `TIER_EN`, `IMPORTANCE_EN` — the only existing translation table |

The UI already carries a few ad-hoc bilingual pairs (`模拟 / SIMULATED`, `风险等级`, `组织者模板`, `网络优先级`, `事实表`).
The plan replaces ad-hoc pairs with one consistent mechanism.

## 2. Where every visible string comes from

Measured from `/api/bootstrap` and `/api/analyze` (probe output, 2026-10-24):

| Surface | Source field(s) | Language available | Gap |
|---|---|---|---|
| Tabs, headings, hints, buttons, placeholders, About prose | `index.html` | English only | needs dictionary |
| Event card (5) | `name`, `time_text`, `airport`, `importance` | `name`=EN + `name_zh`; `time_text`=ZH + `time_en`; `airport`=ZH + `airport_en`; `importance`=ZH + `importance_en` | **inconsistent base language** |
| Airport select | `airport.name`, `airport.tier` | `name`=ZH + `name_en`; `tier`=ZH + `tier_en` | UI shows Chinese only |
| Rules table (12) | `topic`, `trigger`, `action`, `escalate_to` | ZH + `_en` for each | fine, just unused |
| Exam chips (15) | `question_en`, `label` | EN + `question_zh`, `*_zh` | fine |
| 17 output fields | `fields[].label_en` + `label_zh`; `value` | labels bilingual; **values mostly EN but contain ZH fragments** | `f04` time (`第4天下午14:00`), `f08` unknown items, `f05` weather quote, `f17` mixed |
| 3 message drafts | `messages.{ops,airport,passengers}` | English, prefixed `模拟 / SIMULATED` | needs ZH translation |
| Detector card | `comparisons[].label`, `detail`, `verdict` | English | needs ZH |
| Detector table (192 rows) | `airport`+`airport_en`, `tier`+`tier_en`, `verdict` | bilingual | verdict/tier need pairing |
| Network map (8) | `airport`(ZH), `airport_en`, `importance_en`, `reason` | EN reason + ZH names | map labels show short EN only |
| Facts card | `facts[].text` | English, but embeds `大型机场`, event weather ZH text | needs ZH + cleanup |
| Exam results | `runs[].question/expected/forbidden` | mixed — verify at runtime | needs pairing |
| Feedback log | `rec_id`, `result` (already EN via `RESULT_EN`), `reason`, `final_action` | ZH seeds | needs EN |
| Footer / badge | `模拟 / SIMULATED` | already bilingual | keep exactly |

**Key finding:** payloads are bilingual but **not uniform** — sometimes the English text is the base field (`name`, `type`, `source`) with a `_zh` twin, sometimes the Chinese is the base (`airport`, `topic`, `weather_text`, `reason`) with an `_en` twin. Any implementation must use an explicit pair table, never suffix guessing.

## 3. Requirements → design rules

- **R1 Switch** — one control switches the whole UI between English and 中文 instantly, no reload, persisted (`localStorage`), deep-linkable (`?lang=zh`).
- **R2 Entities always bilingual** — airport names (and other key terms: verdict, tier, importance, role) show **both languages at once**, in both modes. Never one language only.
- **R3 Single-language inputs** — user-typed text and Chinese-only organizer text are translated for display, **marked as translated**, with the **original shown on hover** (and in `aria-label`).
- **R4 Honest translation** — two qualities: `reviewed` (an authoritative pair or curated dictionary) and `auto` (rules/glossary). `auto` carries a `≈` marker. Unknown text degrades to the original, never invents.
- **R5 Offline** — stdlib + vanilla JS only. No network, no model, no new dependencies.
- **R6 Display-only** — translation never alters request payloads, the feedback JSONL, the checker, the exam or any number. Numbers, IDs (`EVT001`, `RULE003`, `F03`, `f04`), source codes (`SIM-BASE`, `[FACT: …]`) are never translated.
- **R7 模拟** — `模拟 / SIMULATED` stays verbatim in every language.
- **R8 Accessible** — correct `lang` attributes, keyboard-operable toggle, translated spans reachable by screen readers with the original included.

## 4. Architecture

```
index.html  ── data-i18n="key" ─────────────┐
                                            ├──> i18n.js ──> t("key")  (UI chrome)
app.js (renderers) ── tr(value) / bi(en,zh) ┘        │
                                                     └──> EXACT / TERMS / PATTERNS (data text)
server.py  ── STATIC_FILES + "/i18n.js" (one line)   └──> quality badge + title=原始文本
```

**New file `app/static/i18n.js`** (loaded *before* `app.js`):

```js
const UI = { en: { tab.assistant: "Assistant", ... ~120 keys }, zh: { ... } };
const EXACT = { zh2en: { "第4天下午14:00": "Day 4, 14:00 (afternoon)", ... }, en2zh: { ... } };
const TERMS = [ ["国际机场", "International Airport"], ["航班", "flight"], ... ];   // longest match first
const PATTERNS = [ [/^第(\d+)天下午(\d{1,2}:\d{2})$/, "Day $1, $2 (afternoon)"], ... ];
```

Public API (stable contract for `app.js`):

| Function | Purpose |
|---|---|
| `getLang()` / `setLang("en"\|"zh")` | read/apply language; `setLang` persists + applies + emits `t3:langchange` |
| `t(key, vars)` | UI string for the active language |
| `applyStatic(root)` | fills `[data-i18n]`, `[data-i18n-title]`, `[data-i18n-placeholder]`, `[data-i18n-aria]` |
| `pair(obj, {en, zh})` | picks the requested language from an explicit field pair; falls back and marks `auto` |
| `tr(text)` | returns `{html, text, quality, original, translated}` for a free-text string |
| `bi(en, zh)` | HTML for an always-bilingual entity: `EN · 中文` |
| `bilingualizeEntities(text)` | appends the other-language form after the first mention of each airport in long text |

**Rendering model.** All renderers are already pure functions of `state`. `setLang` calls `applyStatic()` then re-renders from cache (`state.bootstrap`, `state.analysis`, `state.ranking`, `state.network`, `state.exam`, `state.feedback`) — no refetch, no reload, message tab and selected event preserved.

**Server change (only one).** `STATIC_FILES` must serve the new file:

```python
"/i18n.js": "i18n.js",
```

Nothing else in `server.py` changes.

## 5. Translation pipeline (per string, in order)

1. **Authoritative pair** — the object carries both languages (see table below): use the requested one; if absent, use the other and mark `auto`.
2. **Curated exact match** — `EXACT` dictionary (fixed organizer strings: 5 event texts, 12 rules, 15 test questions, 3 feedback seeds, 4 DQ notes, 10 field labels, 17 field values, 3 message templates, detector labels). Quality `reviewed`.
3. **Pattern rules** — deterministic formats: `第N天下午H:MM`, `第N天`, months `2025-08`, percentages/pp, `待处理/已处理`, `有效/无待`. Quality `auto`.
4. **Glossary compose** — longest-match term substitution over `TERMS`; unmatched CJK fragments stay in the original script inside the translated string so the reader can see what was not translated. Quality `auto` (`≈`).
5. **No CJK / no match** — return unchanged (`translated:false`).

**Pair table (explicit, verbatim from the probe):**

| Object | Chinese base | English twin |
|---|---|---|
| event | `airport`, `time_text`, `weather_text`, `ops_text`, `notes`, `known`, `unknown`, `importance` | `airport_en`, `time_en`, `weather_en`, `ops_en`, `notes_en`, `known_en`, `unknown_en`, `importance_en` |
| event (reverse) | `name_zh` | `name` |
| airport | `name`, `tier`, `city`, `province`, `importance` | `name_en`, `tier_en`, `city_en`, `province_en`, `importance_en` |
| rule | `topic`, `trigger`, `checks`, `action`, `escalate_to`, `forbidden` | `*_en` each |
| test | `question_zh`, `type_zh`, `expected_zh`, `forbidden_zh` | `question_en`, `type`, (add `expected_en`/`forbidden_en` if absent → translate) |
| output field | `label_zh` | `label_en` |
| network / ranking row | `airport`, `tier`, `importance` | `airport_en`, `tier_en`, `importance_en` |

If a twin is missing in the payload, the plan **forbids inventing it in the engine** — the client translates via layers 2–4 and marks `auto`.

## 6. Always-bilingual entities (R2)

`bi(en, zh)` renders `<span class="bi"><span lang="en">EN</span><span class="bi-sep">·</span><span lang="zh-Hans">中文</span></span>`, e.g. **Hailing International Airport · 海陵国际机场**.

Apply in both modes at:

- event cards (`airport`, `importance`), selected hint, status lines, toasts
- airport `<select>` (`name_en · name`), detector table (already two lines — unify), network table, ranking table
- network map node label (two lines: EN then 中文), node `<title>`/`aria-label`, chart legend, detector card header
- rule table "Escalate to" (`Operations Lead · 运营负责人`), verdict chips, tier cells, risk level (`Medium · 中` — already)
- long text: `bilingualizeEntities()` on facts, field values, messages, reasons — appends `（海陵国际机场）` after the first English mention (and the reverse in ZH mode)

## 7. Translated-input UX (R3)

For any string that came from the other language and was translated:

```html
<span class="i18n-tr" tabindex="0" title="原文 / Original: 第4天下午14:00"
      aria-label="Translated from Chinese. Original: 第4天下午14:00">Day 4, 14:00 (afternoon)<sup class="i18n-badge">译</sup></span>
```

- `译` badge in EN mode, `translated` in ZH mode; `≈` added when quality is `auto`.
- Dotted underline; original in native `title` (satisfies "hover text") **and** in `aria-label` for keyboard/screen-reader users.
- A short legend in the **About** tab: reviewed vs auto, and the rule that originals are never lost.
- Messages (`<pre>`) stay plain text: badge lives in the card header (`"3 audience drafts · translated from English · 译"`), original available via a "Show original" toggle — avoids polluting copy-to-clipboard.

## 8. Phases and acceptance

| Phase | Work | Done when |
|---|---|---|
| **P0 Baseline** | record `python -m unittest discover -s tests` (expect 40/40) and `python tests/run_tests.py --writer-mode offline` (21/21) | numbers written into the log |
| **P1 Chrome** | `UI` dictionary (~120 keys), `data-i18n` on all 67 nodes, toggle in `.topbar`, persistence, `?lang=`, `<html lang>`, `document.title` | switching on every tab leaves no English noun in ZH mode except entities/IDs |
| **P2 Entities** | `bi()` and `pair()` applied per §6 | an airport is never shown in one language anywhere |
| **P3 Data text** | `EXACT`, `PATTERNS`, `TERMS`, `tr()`, badges, About legend, `bilingualizeEntities()` | ZH input in EN mode shows translated + `译` + original on hover; EN output in ZH mode likewise |
| **P4 Proof** | `tests/test_i18n.py`, screenshots `evidence/screenshots/lang-assistant-en.png`, `lang-assistant-zh.png`, `lang-detector-zh.png`, `lang-translated-hover.png`; D02/D08 note | tests green, screenshots committed |

**Acceptance checklist**

1. Toggle switches all 5 tabs without reload; choice survives refresh; `?lang=zh` works.
2. No airport name appears in only one language, on any tab, in either mode.
3. Every translated string shows the marker and exposes the original on hover and to screen readers.
4. No numbers/IDs/source codes/`模拟` are translated or reformatted.
5. Existing suites unchanged: 40/40 unit, 21/21 exam; checker behaviour identical.
6. App still runs with zero network calls and zero new packages.
7. `git diff` touches only: `app/static/index.html`, `app/static/app.js`, `app/static/styles.css`, `app/static/i18n.js` (new), `app/server.py` (one line), `tests/test_i18n.py` (new), docs/log files.

## 9. Tests (stdlib only)

`tests/test_i18n.py`, four groups:

1. **Key coverage** — parse `i18n.js` with a regex; every `data-i18n*` key in `index.html` and every `t("…")` in `app.js` exists in both `en` and `zh`. No empty values.
2. **Pair integrity** — from `pipeline.bootstrap()`: every event has `name`+`name_zh`, every airport `name`+`name_en`, every rule `topic`+`topic_en`; every analyzer field has `label_en`+`label_zh`; the 3 messages are non-empty.
3. **Translation behaviour** — pure-Python mirror of the pattern rules for `第4天下午14:00 → Day 4, 14:00 (afternoon)`; ensure the JS `PATTERNS` table contains the same cases (regex-extracted), so JS and Python cannot drift.
4. **Whitelist** — `/i18n.js` is present in `STATIC_FILES`.

Manual: `python app/server.py`, then walk the checklist above at `http://127.0.0.1:8803`.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Payload language is inconsistent (base field flips) | explicit pair table + test group 2; never infer by suffix |
| Re-render loses state (analysis, message tab, selection) | re-render from `state`, never refetch; keep `state.msgTab`/`selectedEvent` |
| Glossary mangles proper nouns | entity names only from authoritative pairs; glossary never rewrites tokens inside `[FACT: …]`, IDs or numbers |
| Translated text leaks into API payloads / feedback | `tr()` is display-only; explicit rule R6 + code review |
| Duplicated strings drift between HTML and JS | one `UI` source; `applyStatic` owns static nodes |
| Scope creep into engine/server | only the single `STATIC_FILES` line is allowed |
| Judge sees machine translation as low quality | curated `EXACT` covers all demo content; `≈` marks anything weaker; About tab explains |

## 11. Explicitly out of scope

Live-LLM translation, server-side rendering, translating exported JSON/Excel, new API endpoints, dependency installs, re-authoring organizer data, translating user input before it is sent to `/api/analyze` (the engine must keep seeing the original).
