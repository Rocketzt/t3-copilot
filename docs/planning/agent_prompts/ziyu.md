# Agent prompt — Ziyu (checker) — optional, small run

Optional: run it only if you have usage to spare. The checker is small enough to write by hand from this spec, and
then the spec below is your checklist. Copy the box into your agent, in the repo root, on branch `ziyu`.

````text
You are working unattended in the git repo "t3-copilot" (HackSHSID 2026, Track 3). You are on branch `ziyu`.
Build one module and its tests. Do not wait for me. If blocked, write it down and stop. Do not guess.

READ FIRST: ROLES.md, CONTRACT.md §6 (the "output" and "check" shapes, and "Rules for the writer") and §11,
docs/planning/ERRATA.md, EXECUTION_PLAN.md §3.3.

HARD RULES
- Edit ONLY engine/checker.py, tests/test_checker.py and docs/project/log/ziyu.md.
- Python 3.10+ standard library only. Deterministic: no LLM calls.
- Commit with a message ending in "Assisted-by: <your agent name>", then run `git push origin ziyu`. Never push to
  main.

BUILD engine/checker.py
`check(output, facts) -> {"passed": bool, "checks": [{"id","name","status":"pass|fail","detail"}],
"failures": [...]}`
A check fails, naming the offending text, when any of these happens:
C01 any of the 17 fields f01–f17 is missing or empty;
C02 a number in a field or message is not in facts["numbers"]. Before comparing, mask the IDs (SIM-*, RULE0xx,
    EVT0xx, TEST0xx, Fxx), dates, times, the field keys and list numbering. Match on the value, with a tolerance of
    0.01;
C03 a [FACT: X] tag names a source not in facts["sources"];
C04 committed-action wording: 已取消 / 已发送 / 已放行 / 已通知, or "has been cancelled/sent/released/dispatched",
    or the assistant deciding to cancel/release/dispatch/maintain/compensate outside f12;
C05 the passenger message states a delay or cancellation as fact, or lacks "draft"/草案 and an "official channels"
    phrase;
C06 two of the three messages are identical;
C07 PII: mobile numbers (1[3-9]\d{9}), 18-character ID numbers, email addresses;
C08 "模拟" is missing from f13, f14, f15 or f17;
C09 facts["conflict"] is true but the risk is not "Can't tell"/无法判断;
C10 weather data is missing for the month (facts["missing_data"]) but the output does not say so;
C11 facts["feedback_matches"] is non-empty but neither f10 nor f13 mentions the prior feedback;
C12 a causal overclaim: "weather caused", "caused by weather", "due to the weather" stated as fact, or 天气导致;
C13 f12 lacks the human-decision categories (cancellation, release, dispatch, maintenance, compensation).

TEST tests/test_checker.py (stdlib unittest)
- If fixtures/output_EVT001.json and fixtures/output_bad.json exist (Jonathan's), use them together with
  fixtures/factsheet_EVT001.json or mock_factsheet_EVT001.json. Otherwise build small inline examples.
- Required: a good output passes every check; the bad output fails C02 and names "20"; one failing example per
  check C01–C13.
- Run `python -m unittest tests.test_checker -v` and log the real result.

FINISH
Add an entry at the top of docs/project/log/ziyu.md with the result, the re-run command, anything BLOCKED, and an
"AI:" line. Commit and push.
````

Note: `tests/test_checker.py` sits in Jason's `tests/` folder. It is the one test file Ziyu owns. Jason's runner
must not overwrite it.
