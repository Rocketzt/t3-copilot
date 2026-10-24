# AI usage log

Compiled from every **AI:** entry in `docs/project/log/jason.md`, `jonathan.md`, and `ziyu.md` through the integrated exam run. Entries below preserve each contributor’s wording; the logs contain the verification details. Raw outputs are kept under `evidence/ai/` where available.

## Jason

- **2026-10-24 16:56 — Integrated exam passes; submission evidence updated:** Codex populated D03 from the runner JSON, checked detector numbers, entered simulated feedback through the append-only helper, compared real EVT005 outputs, compiled log evidence, and drafted the submission text; all reported scores were taken from command output.
- **2026-10-24 16:42 — Network priority view ranks eight airports from detector context:** Codex implemented the deterministic view, checked its output against detector rows, and wrote the regression tests.
- **2026-10-24 16:31 — Hostile operational request is neutralized in the fact sheet:** Codex updated fact presentation, added the regression test, checked the fixture output, and recorded the actual test and exam results.
- **2026-10-24 16:18 — Fact sheets whitelist detector signals and event-text numbers:** Codex updated the fact builder, added regression tests, regenerated fixtures, and checked the test and diff results.
- **2026-10-24 16:15 — ClawsGO cross-check agrees; D05 and D03 prepared:** Codex wrote the comparison script and report, checked the seed and fixture values for D05, and prepared the D03 tables without inventing results.
- **2026-10-24 01:13 — Fact sheets now whitelist all comparison and weather numbers:** Codex added the source-backed facts and regression tests, then regenerated fixtures from the implementation.
- **2026-10-24 00:14 — Build hand-off complete with exam integration pending:** Codex implemented and verified these phases. The self-check fake pipeline is limited to `tests/test_runner_selfcheck.py` and is not an exam result.
- **2026-10-24 00:13 — Phase 3 runner ready; integration run blocked:** Codex implemented the runner and specifications; the fake pipeline was used only in the runner self-check.
- **2026-10-24 00:10 — Phase 2 fact sheets and feedback verified:** Codex implemented and checked this phase against the contract and organizer seeds.
- **2026-10-24 00:06 — Phase 1 detector matches workbook checks:** Codex implemented the export, detector, generated numbers, and tests; kept workbook values as the source of numeric claims.
- **2026-10-23 23:52 — Setup completed on jason:** Codex handled setup and verified the backup against Git blob hashes.

## Jonathan

- **2026-10-24 16:30 — Repo updated; self-check found 13 small issues; plain-language plan written:** DeepSeek Harness — updated the repo, ran the checks, probed the checker and wrote the plan.
- **2026-10-24 14:05 — Merged main; pipeline uses Jason's real engine; exam 0/21 (checker-only failures):** DeepSeek Harness — merged, rewired the pipeline/writer/QA, ran the exam and wrote this entry.
- **2026-10-24 13:40 — PUSH COMPLETED: `jonathan` is on GitHub at `466f2d6`:** DeepSeek Harness — retried the push, diagnosed auth/email blocks, rewrote the author emails, pushed and wrote this entry.
- **2026-10-24 00:58 — FINISH: unattended build complete; 15/15 endpoint self-test passed:** DeepSeek Harness — executed setup, generated fixtures, wrote the writer/pipeline/QA/server/UI, ran the self-test and this log.
- **2026-10-24 00:52 — Phase 3: five-tab offline UI:** DeepSeek Harness — wrote the UI and checked it.
- **2026-10-24 00:50 — Phase 2: pipeline, bounded QA and stdlib server:** DeepSeek Harness — wrote the pipeline, QA and server.
- **2026-10-24 00:45 — Phase 1: workbook fixtures and offline template writer:** DeepSeek Harness — generated the fixtures and wrote the writer.
- **2026-10-24 00:40 — Setup for the unattended build: branch, merge, venv, port 8803:** DeepSeek Harness — executed the setup commands and wrote this entry.

## Ziyu

- **2026-10-24 03:36 — C02 false positive fixed: letters+digits identifiers no longer read as numbers:** OpenCode (GLM-5.3) applied the general identifier mask and the two new test cases as specified; no other check was loosened.
- **2026-10-24 03:17 — C05 false positive fixed: "official airline and airport channels" now accepted:** OpenCode (GLM-5.3) applied the one-pattern fix and the new test as specified; no other checks were loosened.
- **2026-10-24 03:05 — Checker built: all 13 rules C01-C13 block on cue and pass on a good output:** OpenCode (GLM-5.3) implemented the checker and tests unattended from the ziyu.md prompt; I reviewed the spec compliance (mask list, tolerance, "20 points" negative case) and kept the good/bad inline outputs number-clean against both fact sheets.

## Earlier setup provenance

The existing repository AI usage note also records two setup items that predate these three individual logs:

- 2026-10-23 — Rocketzt used Claude Code to review organizer materials, draft the shortlist PDF, check workbook numbers, and set up the repository layout. The layout was kept; the numbers were recomputed by script.
- 2026-10-23 — A teammate used an AI assistant to draft `EXECUTION_PLAN.md` and `CONTRACT.md`. Errors were recorded in `docs/planning/ERRATA.md`; the teammate and tool name remain unconfirmed in the earlier note.
