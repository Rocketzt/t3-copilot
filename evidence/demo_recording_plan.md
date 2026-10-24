# Fallback demo recording — plan (no video file exists yet)

**Status: NO VIDEO FILE WAS CREATED.** There is no `evidence/demo-fallback.mp4` and no other
recording in this repo. This document is the exact script + manual procedure so a human can
record the real app in one take. Nothing here is a mock-up, and no video may be claimed to exist
until the file is actually recorded and verified.

Why no file was produced (tooling survey, 2026-10-24 ~16:30 +0800, this machine):

| Check | Command | Result |
|---|---|---|
| ffmpeg on PATH | `where.exe ffmpeg` | not found (exit 1) |
| ffmpeg common dirs | `C:\ffmpeg`, `%LOCALAPPDATA%\Microsoft\WinGet\Links`, `C:\ProgramData\chocolatey\bin`, scoop shims, `C:\Program Files*` recursion | none found |
| OBS / ShareX / Camtasia / Bandicam | `Get-Command obs64`; standard install paths | none installed |
| winget packages | `winget list` filtered for ffmpeg/OBS/HandBrake/VLC/ShareX/screen recorders | none installed |
| Python video libs | bundled Python 3.x: `av`, `imageio`, `imageio_ffmpeg`, `moviepy`, `cv2` | all absent; only `Pillow` 12.3.0 (no video encoder) |
| Browser | headless Edge `Edg/155.0.4283.62` (CDP works), Chrome installed | frame *source* only, cannot write a video file |
| Game Bar | `HKCU:\System\GameConfigStore\GameDVR_Enabled = 1`; `Microsoft.GamingApp` appx present; Windows 11 build 26300 | manual Win+Alt+R recording likely available **with a human at the desktop** |

The automatic route was considered and is *technically* possible but was not attempted because it
cannot produce an acceptable fallback: browser CDP `Page.startScreencast` can capture real frames
from the real app (this is a genuine screen recording, not a fake), but with **no ffmpeg/encoder on
this machine** they can only be written as an animated WebP/GIF via Pillow — silent, no narration,
large, and not an `.mp4` a judge can play in a normal player. If the Lead wants that silent
animation as an extra artifact, say so and it can be produced after the merge; otherwise record
manually with Game Bar or OBS (below).

---

## 1. Script — 3:45 target (compressed from EXECUTION_PLAN §9.1, 5:00)

Copy the §9.1 beats one-to-one; only the intro/typing are tightened. One take, no cuts.
Driver = the person whose machine shows the app; narrator = Jason.

| Time | Who | Click path | Must be visible on screen | Speaker line (say ≈ this) |
|---|---|---|---|---|
| 0:00–0:20 | Jason | Nothing; app already open on `http://127.0.0.1:8811/?tab=assistant` | `模拟 / SIMULATED` in the top bar; 5 event cards; `engine: real` badge | "An assistant for airport disruptions at a **fictional** airline. Everything here — airports, events, numbers — is simulated." |
| 0:20–1:05 | Jonathan (drives) | Fill the new-event form: Airport = `海陵国际机场 / Hailing International Airport (Large airport)`, Time window = `Day 4, 14:00; next 6 hours`, Weather = `Heavy rain and gusts next 6 hours`, Operations = `Morning normal, afternoon flights concentrated`, Importance = `High`; Writer stays `Offline template` → **Analyze new event** | Result page appears: risk card **Medium / 中**, detector card 3 comparisons, 17-field advice starting to render | "Type a new event — Hailing, heavy rain plus gusts for six hours on a busy afternoon. In seconds: risk **Medium**, the detector card, and the organizer's 17 fields." |
| 1:05–1:40 | Jonathan | Scroll to Fact sheet → `Assumptions to Verify` → `First Action` → `Decisions Requiring a Human` (`f12`) | `FACT · SIM-*` chips, exactly **one** ASSUMPTION chip, UNKNOWN gaps, `f09 First Action`, `f12` human-only decisions | "Every claim is sourced or labelled: FACT with a source ID, ASSUMPTION, or UNKNOWN. First action is to confirm ground-support capacity; cancellation and the formal passenger notice stay human decisions." |
| 1:40–2:05 | Jonathan | Click the three message tabs: **Operations → Airport coordination → Passengers** (`#msg-tabs`) | Three visibly different drafts; passenger draft says "possible delays … check official airline and airport channels"; each carries 模拟 / SIMULATED and "draft, not an official notification" | "Three audience drafts — internal ops, airport coordination, passengers. Different tone, same facts, and the passenger text says possible delays, never a confirmed delay." |
| 2:05–2:35 | Ziyu | Click **Detector** tab (`/?tab=detector`) | Stat cards `192 / 12 / 13 / 2 / 1`; Hailing vs Yunchuan chart with peer line; highlighted 2025-07/08; ranking row Hailing 2025-07 own Δ **−15.62 pp**, YoY **−11.48 pp** | "All 192 airport-months, three comparisons each. 12 official flags, 2 multi-signal, 1 priority: Hailing 2025-07, −15.62 points below its own 12-month average and −11.48 year-on-year. Yunchuan looks similar but is seasonal — **−0.80** year-on-year." |
| 2:35–3:05 | Ziyu | **ONLY IF the checker is merged** (confirm: `/api/health` → `checker_available: true` and the checker card is not "not checked"): back to Assistant, run one analysis with Writer = `Demo bad AI (invented number)` → **Analyze** | Checker card **red / BLOCKED**, the invented number named, "needs human review" fallback | "This writer is deliberately bad: it invents a number. The checker blocks it and names the number — red is the feature, not a failure." **If the checker is NOT merged: skip this beat and say "the checker is still not checked on this branch" — never stage a fake red panel.** |
| 3:05–3:30 | Jonathan | Assistant → select **EVT005** (Human overrule) → **Analyze selected event**; scroll to `Prior feedback loaded` + `f09 First Action` | Prior feedback REC003 `Reject` quoted with the reason; first action reads **"confirm current resources"**; original advice still shown | "Staff rejected the earlier escalation: resources were sufficient, wind within limits. The next similar event quotes that rejection, and the first action changes to confirm current resources. The original is never overwritten." |
| 3:30–3:45 | Jason | Click **Exam** tab → **Run exam** (pre-run result is fine if it was run before recording; see pre-flight) | Summary `15/15 official`, `5/5 own`, results table with expected/forbidden/evidence columns | "15 of 15 official tests plus our own 5 – TEST003 says can't-tell, TEST005 refuses to cancel, TEST011 redacts PII. Fabricated numbers are blocked, not styled over." |
| 3:45 | Jason (close, over the app/About tab) | Nothing; end on the app | `模拟 / SIMULATED` visible; About tab counts | "12 alerts down to 1 priority review, zero fabricated numbers, drafts in seconds — and the decisions stay human. Questions?" |

**The two numbers everyone must know:** **Hailing −15.62 pp** and **Yunchuan −0.80 pp** year-on-year.

## 2. Pre-flight checklist (before hitting record)

- [ ] Lead's server running at `http://127.0.0.1:8811`; `curl http://127.0.0.1:8811/api/health` → `engine: ready`.
- [ ] Branch is the merged build; `engine: real` badge visible; checker state read from `/api/health` and spoken honestly.
- [ ] Window exactly **1440×1000** (`/?tab=assistant`), browser zoom 100 %, bookmarks bar hidden, no dev tools, no notifications.
- [ ] `/?event=EVT001` and `/?tab=detector` load in one click each (deep links merged).
- [ ] Exam already run once (so the results table can be shown instantly) **or** accept the ~10–20 s "Run exam" spinner on camera.
- [ ] Close everything that could pop up (chat apps, updates); mute is fine, microphone tested.
- [ ] Rehearse once without recording; keep the click order identical to §1.

## 3. Manual recording steps

### A. Game Bar (no install; recommended first attempt)

1. Open the app in a normal (non-headless) browser window at 1440×1000.
2. Press **Win+G** to open Game Bar → confirm the Capture widget is pinned → settings: record **system audio off, microphone on**, video quality **Standard/High**, 30 fps.
3. Press **Win+Alt+R** to start recording (or the Capture widget's Record button). A small "recording" bar shows elapsed time — **keep it out of the app's key UI** (top-left is safest).
4. Perform §1 in one take; press **Win+Alt+R** again to stop.
5. Windows saves to `Videos\Captures`; rename to `demo-fallback.mp4` and move it to
   `t3-copilot/evidence/demo-fallback.mp4`, then verify duration (3:30–4:00) and that the `模拟` badge,
   risk card, detector numbers and messages are readable on playback.

### B. OBS Studio (better control, needs install)

1. `winget install --id OBSProject.OBSStudio -e` (confirm network/install with the Lead first — this
   installs software on the user's machine; no other install is needed).
2. New scene → Source **Window Capture** → select the browser window (or **Display Capture**).
   Canvas/resolution 1440×1000 (or 1920×1080 with the window centred), 30 fps, mp4 output
   (`Settings → Output → Recording → MP4`, encoder hardware x264 if available).
3. Audio: microphone; system audio optional (off preferred).
4. Start Recording → perform §1 → Stop. Copy the file to `t3-copilot/evidence/demo-fallback.mp4`,
   verify playable + duration 3:30–4:00 + readable text.

### C. If neither works (e.g. Game Bar blocked by policy)

Record with any installed screen recorder the same way, or fall back to **live demo + screenshot
slides**: `evidence/screenshots/01`, `02`, `04`, `05`, `06`, `07`, `08` are already 1440×1000 and can
stand in for the demo beats. A live, honest demo with slides is preferable to a fabricated video.

## 4. Shot list (screenshot fallback if a beat cannot be recorded live)

| Beat | Existing still | File |
|---|---|---|
| Intro / product | Assistant page, badge, picker | `evidence/screenshots/01-assistant.png` |
| New event → result | risk card Medium + detector card + fact sheet | `06-assistant-result-interim.png` |
| Evidence / gaps / assumptions | fact sheet close-up, "Large airport", one ASSUMPTION chip | `07-assistant-result-tier-and-assumption.png` |
| 17 fields (f07/f09/f12) | f03 Medium, f05 evidence, f07 chip, f09 first action | `08-assistant-result-f07-chip.png` |
| Detector | 192/12/13/2/1 + chart + ranking | `02-detector.png` |
| Feedback memory | seeded Accept/Edit/Reject records | `04-feedback.png` |
| Exam | results table (post-checker re-capture) | `03-exam.png` (currently initial state) |
| About / limits | DQ notes, 12 rules | `05-about.png` |
| Before/after badge | old `engine: fixtures` | `before/00-assistant-engine-fixtures.png` |

## 5. Honesty rules for whoever records

- Record the **real app** on the merged branch; do not film slides and call it a demo.
- Do not stage the checker red panel unless the checker actually blocks a fabricated number;
  if it is "not checked", say so on camera.
- Do not claim staff-time savings, real CAAC numbers, or measured accuracy.
- Keep `模拟 / SIMULATED` visible at the start and end.
- After recording, update this file's status line: `Status: recorded on <date>, <duration>, <size>`
  plus the tool used, and tell the Lead the file path. Until then, the honest status is:
  **no video file exists.**
