# Tasks

Status: TODO / DOING / BLOCKED / PARKED / DONE. Deadline: **2026-10-24 23:59**.
The build tasks themselves (Z1–Z10, J1–J9, A1–A8) live in `EXECUTION_PLAN.md` §5; this list tracks the rest.
This is a shared file: edit it on `main` only (pull, one small commit, push). Ziyu updates it at each gate.

## Team
- [x] **Decide the default writer** — offline template. `DONE 2026-10-24`: applied consistently (README writer
      modes, every exam run with `--writer-mode offline`); a DECISIONS.md line to copy it verbatim is open
      (`OVERVIEW.md` open question).
- [x] **Fix ERRATA items** — `DONE 2026-10-24` in substance: C3/C4/C5 and C7/C8/C9 are implemented in the code
      and layout, and the remaining plan-text items are marked historical by the top line in
      `docs/planning/ERRATA.md` (the build followed `ROLES.md` and the reviewed code on `main`).
- [ ] **Register** — each member registers on study.standardcas.org with their real name, and confirm all three
      are registered and joined to one project. `TODO` owner: each member
- [ ] **Create project and join** — folded into the registration check above until someone confirms it happened.
      `TODO` owner: leader + members
- [x] **Install build packages** — `DONE 2026-10-24` (clean-clone check): a fresh venv installs
      `requirements.txt` from PyPI without errors (Pillow 13.0.0, openpyxl 3.1.5, pandas 3.1.0); the repo `.venv`
      remains untouched and stdlib-only, since app/engine/tests need nothing.
- [ ] **Move the last two organizer PDFs** — close the Track 1/2 PDFs and move `HackSHSID 2026/` into
      `organizer_materials/` (both are git-ignored either way). `TODO` owner: Rocketzt

## Submission
- [ ] **UI polish** — last look at all five tabs before screenshots. `TODO` owner: Jonathan
- [ ] **Fresh screenshots + thumbnail** — re-capture the checker pass, the bad-AI block and the 21/21 exam after
      the UI polish; set the thumbnail in `docs/SUBMISSION_DRAFT.md`. `TODO` owner: Jonathan + Ziyu
- [ ] **Fill the submission form** — title, short description, track, thumbnail, description, repo link, testing
      evidence, AI statement (text is ready in `docs/SUBMISSION_DRAFT.md`; from `docs/AI_USAGE.md`). Only one
      person edits at a time. `TODO` owner: Jason (ROLES.md)
- [ ] **Confirm registration** — all 3 members registered on study.standardcas.org. `TODO` owner: whole team

## Done
- [x] **Teammates are repo collaborators** — `DONE 2026-10-23`: chrochrohoho and JasonXiao7, checked through the GitHub API.
- [x] **Confirm Track 3 and roles** — `DONE 2026-10-23` (DECISIONS.md, `ROLES.md`).
- [x] **Settle file owners** — `DONE 2026-10-23`: `ROLES.md` is the single owner table (ERRATA C6).
- [x] **Repo skeleton** — `DONE 2026-10-23` (LOG.md): directories, a README in each, deliverable stubs,
      `.env.example`, `requirements.txt`, AI-use log.
- [x] **Review EXECUTION_PLAN.md and CONTRACT.md** — `DONE 2026-10-23` (`docs/planning/ERRATA.md`).
- [x] **README** — `DONE 2026-10-23`: what it is, status, layout, planned commands, simulated-data note.
- [x] **AI-use log started** — `DONE 2026-10-23` (`docs/AI_USAGE.md`); keep adding rows.
- [x] **Public GitHub repo** — `DONE 2026-10-23` (LOG.md): https://github.com/Rocketzt/t3-copilot, public, `main` pushed.
- [x] **Review PLAN.md** — `DONE 2026-10-23` (LOG.md). PLAN.md was later removed as superseded.
- [x] **Review organizer materials** — `DONE 2026-10-23` (LOG.md): all files read; deadline is 2026-10-24 23:59.
- [x] **Set up project records** — `DONE 2026-10-23`.
