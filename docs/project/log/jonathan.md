# Work log — Jonathan (product and integration)

Only Jonathan edits this file, so it never conflicts on merge. Newest entry first, written the same day as the work.
Team-level events (gates, merges, submission) go in `../LOG.md`.

Entry format (copy for each new entry):

```markdown
## YYYY-MM-DD HH:MM — <what was found or finished, not just what was done>

**Setup:** what you did, which files/commit, inputs and settings, how you checked it.
**Result:** the outcome, with numbers and how many cases; what changed because of it.
**Anomalies:** anything surprising, failed or skipped ("None." if none).
**AI:** (only if an AI tool helped) tool, what it did, what you kept or changed.
```

---

## 2026-10-24 00:40 — Setup for the unattended build: branch, merge, venv, port 8803

**Setup:** Read `README.md`, `ROLES.md`, `CONTRACT.md`, `docs/planning/ERRATA.md` and `EXECUTION_PLAN.md` §3/§9.
`git status` showed no changes to tracked files (only two untracked planning notes, which are not part of this
build). `git switch jonathan` succeeded (the repo had a local `Jonathan`; Git resolved it to the same ref) and
`git merge origin/main` reported "Already up to date" — `main` at `f70aecf` is an ancestor of the branch. Python is
**3.12.10**; there was no `.venv`, so I created one and ran `.venv\Scripts\python -m pip install -r requirements.txt`.
Port **8803 was free**, so the default port is 8803 (no `T3_PORT` override needed).
**Result:** The build can proceed; the app itself needs only the standard library. Fixtures are generated from
`Track 3 Data.xlsx` with the machine's bundled `openpyxl` (build-time only), so the runtime does not depend on the
pip install.
**Anomalies:** The pip install made no progress for ~20 minutes and was cancelled — PyPI is unreachable from this
network; `.venv` therefore has no third-party packages (fine for the app). `git fetch origin` and `git ls-remote`
failed twice with "connection reset"/timeout to `github.com:443`, while `https://api.github.com` answered 200; there
is no `gh` CLI and Git Credential Manager holds no GitHub credential, so a remote push may need the API route.
**AI:** DeepSeek Harness — executed the setup commands and wrote this entry.

