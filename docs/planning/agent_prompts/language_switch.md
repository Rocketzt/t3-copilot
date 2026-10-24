# Agent prompt — language switch (EN / 中文)

**How to use:** open a new agent tab in the repo root (`D:\下载\HackSHSID 2026\t3-copilot`), on branch `jonathan`, and paste
**Box A**. It prepares the branch, records the baseline, then does the work described in **Box B** and the plan file.
The design source of truth is [`docs/planning/LANGUAGE_SWITCH_PLAN.md`](../LANGUAGE_SWITCH_PLAN.md) — read it before coding.

---

## Box A — paste this first

````text
You are working unattended in the git repo "t3-copilot" (HackSHSID 2026, Track 3), branch `jonathan`.
Goal: add a two-way English / 中文 language switch to the web app, with bilingual airport names and
translated single-language inputs that are visibly marked and expose their original on hover.

SETUP (stop and report if any step fails; never discard files, never force)
1. `git status`. If tracked files have uncommitted changes, STOP and tell me exactly which files.
2. `git fetch origin` then `git merge origin/main`. If that conflicts, `git merge --abort`, STOP and tell me.
3. Record the baseline, and write the numbers down for the final report:
   - `python -m unittest discover -s tests`           (expected 40/40)
   - `python tests/run_tests.py --writer-mode offline`  (expected official 15/15, own 5/5, negative 1/1)
   If a baseline number differs from these, STOP and tell me.
4. Start the app once to confirm it serves: `python app/server.py` (port 8803, open http://127.0.0.1:8803,
   then stop it). Do not leave a server running.

THEN
5. Read, in this order: README.md, ROLES.md, docs/planning/LANGUAGE_SWITCH_PLAN.md (the whole thing),
   app/static/index.html, app/static/app.js, app/static/styles.css, app/server.py (only the STATIC_FILES block),
   engine/i18n.py.
6. Implement the plan in Phases P1–P4, in order. After each phase, re-run the unit tests and keep them green.
7. At the end: commit on `jonathan` (do NOT push), then print the report described at the bottom of Box B.
````

---

## Box B — the build prompt

````text
You are implementing the "Language switch (EN / 中文)" plan for T3 Ops Copilot. Work offline, with the Python
standard library and vanilla JavaScript only. Work through Phases P1–P4 in order. Do not wait for me; if something
blocks you, write it down and continue with the next item you can finish.

READ FIRST
- docs/planning/LANGUAGE_SWITCH_PLAN.md — the design. §2 inventory, §3 rules R1–R8, §5 pipeline, §6 entity rule,
  §7 UX, §8 acceptance, §9 tests. Follow it; do not redesign it.
- app/static/index.html (297 lines), app/static/app.js (814 lines), app/static/styles.css (357 lines).
- engine/i18n.py for the authoritative airport names. engine/pipeline.py only to understand payload shapes.

HARD RULES
- You may edit ONLY these paths:
  - app/static/i18n.js            (new file)
  - app/static/index.html
  - app/static/app.js
  - app/static/styles.css
  - app/server.py                 (ONE line only: add "/i18n.js": "i18n.js" to STATIC_FILES)
  - tests/test_i18n.py            (new file)
  - docs/D02_Prototype.md, docs/D08_Reproducibility.md, docs/project/log/jonathan.md   (short notes only)
- Do NOT touch: engine/*, app/server.py beyond that one line, data/*, tests/* other than the new file, ROLES.md,
  CONTRACT.md, or any other member's files or logs.
- Do NOT install packages, call the network, add a build step, or introduce a framework. stdlib + vanilla JS only.
- Do NOT translate or reformat: IDs (EVT001, RULE003, TEST007, DQ001, F03, f04), source codes (SIM-BASE, SIM-SCALE,
  SIM-WEATHER), `[FACT: …]` / `[ASSUMPTION]` / `[UNKNOWN]` / `[HUMAN]` tags, any number, dates, percentages,
  or the string `模拟 / SIMULATED` (it stays verbatim in both modes).
- Translation is DISPLAY-ONLY. Never change a request body sent to /api/analyze, /api/ask or /api/feedback;
  never rewrite the feedback JSONL; the checker and the exam must behave exactly as before.
- Keep the app working when `/api/bootstrap` fails: the page must render with English defaults.

PHASE P1 — UI chrome
1. Create app/static/i18n.js with:
   const UI = { en: {...}, zh: {...} };   // flat keys, ~120 entries, no duplicate keys
   const I18N_DEFAULT = "en";
   function getLang(); function setLang(lang); function t(key, vars); function applyStatic(root);
   - getLang: ?lang= (zh|en) > localStorage "t3.lang" > <html lang> > "en".
   - setLang: normalise to "en"|"zh", persist, set document.documentElement.lang (zh-Hans when zh),
     set document.title, call applyStatic(document), dispatch window event "t3:langchange".
   - t: returns UI[lang][key] (substitute {name} style vars), falls back to UI.en[key], then to the key itself.
   - applyStatic: for each [data-i18n] set textContent; [data-i18n-title] set title; [data-i18n-placeholder]
     set placeholder; [data-i18n-aria] set aria-label. It must be idempotent.
2. Add to index.html: <script src="i18n.js"></script> BEFORE app.js; a language control inside `.topbar`:
   <div class="lang-switch" role="group" aria-label="Language">
     <button type="button" data-lang="en" aria-pressed="true">EN</button>
     <button type="button" data-lang="zh" aria-pressed="false">中文</button>
   </div>
   and data-i18n attributes on every static visible string (all 67 nodes: tabs, h1/h2, hints, labels,
   buttons, placeholders, footer, About prose, Exam/Feedback/Detector headings).
3. In app.js: initialise language in init() (before any render), wire the two buttons (click + keyboard),
   listen for "t3:langchange" and re-render from cache: applyStatic(), then renderEventCards(),
   renderAirportSelect(), renderAskChips(), renderAbout(), and if state.analysis renderResult(state.analysis),
   if state.ranking renderDetectorStats()+renderChart(state.chart)+renderRanking(), if state.network
   renderNetwork(state.network), if state.exam re-render the exam table, if state.feedback loadFeedback()
   from cache. Never refetch on toggle; preserve state.msgTab and state.selectedEvent.
4. Add the one STATIC_FILES line in app/server.py.

PHASE P2 — entities always bilingual (rule R2)
1. Add to i18n.js:
   function bi(en, zh)            -> HTML: <span class="bi"><span lang="en">EN</span><span class="bi-sep">·</span>
                                     <span lang="zh-Hans">中文</span></span>, escaping both inputs.
   function pair(obj, spec)       -> { text, translated, quality } using an EXPLICIT field table:
        event:   airport/airport_en, time_text/time_en, weather_text/weather_en, ops_text/ops_en,
                 notes/notes_en, known/known_en, unknown/unknown_en, importance/importance_en,
                 name/name_zh (note: English base here)
        airport: name/name_en, tier/tier_en, importance/importance_en
        rule:    topic/topic_en, trigger/trigger_en, checks/checks_en, action/action_en,
                 escalate_to/escalate_to_en, forbidden/forbidden_en
        field:   label_zh/label_en
        row:     airport/airport_en, tier/tier_en, importance/importance_en
     Never infer the language from a field-name suffix at runtime; use this table.
2. Render airports bilingually everywhere: event cards, selected hint, status lines, toasts, the airport
   <select> (value stays the Chinese name; text becomes "name_en · name"), ranking table, network table,
   detector card header, chart legend, and the network map (two-line label: short English, then 中文;
   keep the SVG aria-label and <title> bilingual). Verdict, tier, importance and role names use bi() too.
3. Facts, field values, messages and feedback reasons: run bilingualizeEntities(text) so the first mention of
   each airport is followed by the other-language name in parentheses, e.g.
   "Hailing International Airport（海陵国际机场）2025-08: …". Both modes get this.

PHASE P3 — translated inputs (rules R3, R4)
1. In i18n.js add:
   function tr(text) -> { text, html, translated, quality: "reviewed"|"auto"|"none", original }
   and the data behind it:
   - EXACT: { zh2en: {...}, en2zh: {...} } — curated full-string translations for the fixed organizer content:
     the 5 event name/weather/ops/notes/known/unknown strings, 12 rule topic/trigger/checks/action/escalate_to/
     forbidden, 15 test question/expected/forbidden text, 3 feedback reasons/final actions, 4 data-quality
     descriptions, 17 field values where a Chinese fragment remains (f04 time, f08 items, f17 status), and the
     3 message drafts (EN -> ZH). Quality "reviewed". Use the payload samples you can print with
     `python -c "from engine import pipeline; ..."` to copy the exact source strings; do not invent strings.
   - PATTERNS: deterministic formats, at minimum 第N天下午H:MM -> "Day N, H:MM (afternoon)", 第N天 -> "Day N",
     模拟 -> "", 待处理 -> "Pending", 已处理 -> "Done". Quality "auto".
   - TERMS: a phrase glossary (longest match first) for residual text, covering at least: 机场, 国际机场, 航班,
     旅客, 机组, 天气, 降雨, 风速, 保障, 协同, 资源, 风险, 延误, 取消, 调机, 放行, 维护, 赔偿, 信息, 数据,
     来源, 基线, 异常, 信号, 置信度, 月度, 运行, 决策, 人工, 审批, 建议, 草案, 通知, 原因, 记录, 复核, 缺失,
     未知, 待处理, 高, 中, 低. Quality "auto".
   - tr() order: EXACT hit -> PATTERNS -> TERMS compose -> unchanged. Only translate when the text actually
     contains CJK (or, in zh mode, is plain ASCII prose). Never touch numbers, IDs, source codes or tags.
2. Wire tr() into every renderer that displays data text: event cards, detector card, facts card, field values
   (keep rich()/tag chips working — translate the text nodes, not the chip HTML), messages, feedback items,
   ranking/network tables' reason and verdict cells, exam results, and the About rules table.
3. Mark translations (plan §7): a span.i18n-tr with dotted underline, tabindex="0", a sup "+译" (EN mode) /
   "translated" (ZH mode) badge, title="原文 / Original: …" and aria-label carrying the original. For the
   three message drafts, put the marker in the card header and add a "Show original / 显示原文" toggle instead
   of wrapping the <pre> text (copy-to-clipboard must stay clean).
4. Add a short "Translations / 翻译" note in the About tab explaining reviewed vs ≈ auto and that the original
   is always preserved.
5. Add CSS: .lang-switch (+ active/pressed state), .i18n-tr (dotted underline, cursor help), .i18n-badge
   (small sup chip), .bi / .bi-sep (bilingual pair), network two-line label sizing. Reuse existing tokens in
   :root; do not restyle the page.

PHASE P4 — proof
1. tests/test_i18n.py (stdlib unittest only), four groups from plan §9:
   key coverage (both languages, no empties, every data-i18n key and every t("…") present),
   pair integrity on pipeline.bootstrap(), PATTERNS behaviour + JS/Python drift check, STATIC_FILES contains /i18n.js.
2. Run: `python -m unittest discover -s tests` must stay 40/40 plus the new file green.
   Run: `python tests/run_tests.py --writer-mode offline` must stay 15/15 official, 5/5 own, 1/1 negative.
3. With the server running, capture screenshots into evidence/screenshots/:
   lang-assistant-en.png, lang-assistant-zh.png, lang-detector-zh.png, lang-translated-hover.png
   (the hover one must show the 译 badge and the original-language tooltip).
4. Update docs/D02_Prototype.md and docs/D08_Reproducibility.md with a short "Language switch" section
   (how to switch, what is translated vs bilingual, how to verify). Append one entry to
   docs/project/log/jonathan.md in the file's existing format, marking the commit `Assisted-by: DeepSeek Harness`.

VERIFY BEFORE FINISHING
- `git diff --stat` touches only the allowed paths.
- No leftover server process; `git status` shows only intended files.
- Toggle on all five tabs in both directions, with and without `?lang=zh`, and after a hard refresh.
- No airport appears in only one language; every translated string has its marker and original.
- `python -m unittest discover -s tests` and the exam numbers match the baseline.

COMMIT AND REPORT
- One commit (or one per phase) on `jonathan`, message style like the repo's:
  "feat(ui): EN/中文 language switch with bilingual entities and marked translations"
  with the body listing P1–P4 and the test numbers. Do NOT push.
- Final report, at most 12 lines:
  1. baseline vs final test/exam numbers;
  2. files touched;
  3. how the translation quality tiers are represented;
  4. anything not translated and why;
  5. anything BLOCKED or unfinished;
  6. the exact commands I should run to review (server URL, tests, screenshot paths).
````

---

## Review checklist for Jonathan (after the agent finishes)

1. `python app/server.py` → **http://127.0.0.1:8803** — click **EN / 中文** on all five tabs.
2. Confirm no airport name ever appears in one language; confirm `译` + hover original on translated text.
3. `python -m unittest discover -s tests` (40/40 + new) and `python tests/run_tests.py --writer-mode offline` (21/21).
4. `git diff --stat` — nothing outside the allowlist, no engine/server logic change.
5. If it looks right: `git push origin jonathan`.
