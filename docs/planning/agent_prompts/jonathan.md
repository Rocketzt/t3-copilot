# Agent prompt — Jonathan (web app, writer, pipeline)

Copy everything inside the box into your agent, in the repo root, on branch `jonathan`.

````text
You are working unattended in the git repo "t3-copilot" (HackSHSID 2026, Track 3). You are on branch `jonathan`.
Work through Phases 1–3 in order. Do not wait for me. If something blocks you, write it down and move on to the
next item you can do. Do not guess.

READ FIRST: README.md, ROLES.md, CONTRACT.md (all; §6 and §8 are your interface), docs/planning/ERRATA.md,
EXECUTION_PLAN.md §3 and §9.

HARD RULES
- Edit ONLY these files:
  - app/server.py, app/static/*
  - engine/writer.py, engine/pipeline.py, engine/qa.py
  - scripts/make_chart.py
  - fixtures/output_*.json, fixtures/mock_*.json
  - README.md, run_app.bat, run_tests.bat
  - docs/project/log/jonathan.md
  Never edit other files. In particular, Jason owns engine/data, detector, rules, facts, feedback and tests/*, and
  Ziyu owns engine/checker.py. If you need something from their files, write the request in your log.
- Runtime uses only the Python 3.10+ standard library. The web server is stdlib `http.server` on port 8803
  (env T3_PORT). The front end is vanilla HTML/CSS/JS: no CDN, no external fonts, no npm, no build step. It must
  work offline.
- Every page and every generated message shows "模拟 / SIMULATED". All data is fictional.
- Decision support only. The UI and the writer never say a flight has been cancelled, released, dispatched or
  "sent" (no 已取消/已发送/已放行). The passenger draft says "possible delays" and "check official channels".
- No live AI in this run. Build only the offline template writer and the "bad" demo mode. No API keys.
- Set PYTHONIOENCODING=utf-8. Write every file as UTF-8.
- Commit after each phase with a clear message ending in "Assisted-by: <your agent name>". Then run
  `git push origin jonathan`. Never push to main and never merge.

PHASE 1 — mock data + writer
1. If fixtures/factsheet_EVT001.json (Jason's real fact sheet) is missing, create fixtures/mock_factsheet_EVT001.json
   in the exact "facts" shape of CONTRACT §6 for event EVT001 (海陵国际机场 Hailing). Use only these real numbers:
   - 2025-08 completion 73.16% vs own average 84.15% = −10.99 pp;
   - peer −3.66 pp; yoy −9.14 pp;
   - 2025-07 −15.62 pp;
   - sources SIM-BASE, SIM-WEATHER, SIM-SCALE, RULE002, RULE005, RULE007;
   - risk Medium.
   Mark it "mock" inside the JSON.
2. engine/writer.py: `write(facts, event, mode="offline"|"bad") -> output`, in the "output" shape of CONTRACT §6:
   - 17 fields f01–f17, with English and Chinese labels exactly as listed there;
   - 3 messages (ops, airport, passengers), which must differ from each other;
   - tags [FACT: SIM-BASE] / [ASSUMPTION] / [UNKNOWN] / [HUMAN];
   - only numbers that appear in facts.numbers;
   - "模拟" in f13, f14, f15 and f17;
   - feedback_matches, when present, must be mentioned in f10.
   "bad" mode inserts one invented number ("20 points") so the checker demo has something to block.
3. Write fixtures/output_EVT001.json (offline) and fixtures/output_bad.json (bad mode) from the real writer.
   Ziyu tests the checker against them.
Commit and push.

PHASE 2 — pipeline + server
4. engine/pipeline.py: analyze(event_id_or_custom, writer_mode), ask(question, event, writer_mode), bootstrap(),
   detector_ranking(), chart(airports) and run_bad_writer_demo(), returning the JSON shapes in CONTRACT §6 and §8.
   - Import Jason's modules (engine.data, detector, rules, facts, feedback) and Ziyu's engine.checker inside
     try/except.
   - If a module is missing, fall back to the fixtures and set "mode": "fixture" in the result. Never fake a
     checker pass: if checker.py is missing, set check = {"passed": null, "detail": "checker not available"}.
5. app/server.py: every endpoint in the CONTRACT §8 table except /api/export/sheet06 (cut). Also serve static
   files, return JSON errors, and log to the console without Chinese.
6. run_app.bat: starts the server and prints the URL.
Commit and push.

PHASE 3 — the UI (CONTRACT §8 "Static UI spec")
7. app/static/index.html, app.js, styles.css: header with the persistent 模拟 / SIMULATED badge; tabs Assistant
   (default), Detector, Exam, Feedback, About.
   - Assistant: event cards EVT001–005, the New-event form, writer mode (Offline / Demo bad AI), the Analyze
     button with a loading state. Results: the risk card, the detector card (3 comparisons + confidence + the
     month used and why), facts / assumptions / unknowns, the 17-field grid with tag chips, 3 message tabs with
     Copy buttons, the checker panel (red when blocked), and the Accept / Edit / Reject bar posting to
     /api/feedback.
   - Detector: stat cards, the ranking table, and an inline-SVG chart of 海陵 vs 云川 monthly completion with a
     dashed peer line.
   - Exam: a Run button (POST /api/tests/run), summary cards, the results table. If the runner is unavailable,
     show its message.
   - Feedback: records table; About: a short static page.
8. Self-test: start the server, call every endpoint with urllib from a small script, and confirm valid JSON and
   HTTP 200 (or a clear error when a dependency is missing). Put the real results in your log.
Commit and push.

FINISH
Add an entry at the top of docs/project/log/jonathan.md using the format in that file. Include:
- what works and what still runs on fixtures;
- how to start the app;
- the self-test results;
- requests for Jason or Ziyu;
- an "AI:" line naming the agent.
Commit and push one last time.
````
