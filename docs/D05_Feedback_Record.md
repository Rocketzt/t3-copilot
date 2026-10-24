# D05 — Human feedback record

> 模拟 / SIMULATED. All airports, events, feedback and outcomes in this document come from fictional organizer data.

## Organizer seed records

These are the three records in `data/feedback_seed.json`. The English reasons below summarize the original Chinese; the source file remains unchanged.

| Record | Event | Result | Reason recorded by organizer | Final action recorded by organizer |
|---|---|---|---|---|
| REC001 | EVT001 | Accept | No reason was supplied (`null`). | Check airport support capacity and retain a passenger-message draft. |
| REC002 | EVT004 | Edit | The original wording could make passengers think a delay had already occurred. | Make it a risk notice and defer to formal status updates. |
| REC003 | EVT005 | Reject | Operations staff said current on-site resources were sufficient and wind was still manageable. | Do not escalate to High; continue monitoring. |

The seeds are loaded from JSON and labeled `organizer_seed` at runtime. They are read as prior human decisions, not as proof that the same conditions still hold.

## How feedback is retained and recalled

`engine/feedback.py` reads the three immutable seeds, then reads any application records from `data/feedback.jsonl`. `append_record()` writes each new record as one additional JSON line, rejects duplicate record IDs, and redacts personal details before storage. The application code has no edit or delete operation; earlier lines and seed records remain available.

`match()` recalls a record when the event ID matches, when the event has the same airport as an organizer event, or when a record's stored `rule_ids` overlaps the triggered rules. Organizer seeds have no `rule_ids`, so their recall is by event or airport. A match informs the next fact sheet; it does not override a current observation without verification.

## Gaoyuan example in the generated fixture

`fixtures/factsheet_EVT005.json` recalls `REC003` with result `Reject`. Its risk object says `Low` with score `0.75`; its reasons include the human rejection and the instruction to verify resources (`RULE006`). The fact sheet's first action is `confirm current resources`. This lowers the risk relative to the event's rejected High recommendation while keeping current resources subject to confirmation.

## New append-only demonstration records

These three simulated decisions for real organizer event IDs were added with `engine.feedback.append_record()` to `tests/feedback_live_records.jsonl`, an isolated Jason-owned store. The helper labeled each record `source: app`, but no UI user or airline employee submitted them. The production `data/feedback.jsonl` was not changed.

| Record | Event | Result | Reason |
|---|---|---|---|
| LIVE001 | EVT001 | Accept | Risk is separated from formal status and numbers are sourced. |
| LIVE002 | EVT004 | Edit | Clarify that forecast thunderstorm risk is not a confirmed delay. |
| LIVE003 | EVT005 | Reject | Current resources are reported sufficient; verify them before escalation. |

I ran `build_factsheet("EVT005")` before and after pointing its optional feedback path at that store. Before, the real output matched `REC003` (`Reject`); after, it matched `REC003` and `LIVE003` (`Reject`). Both outputs reported risk `Low`, score `0.75`, and first action `confirm current resources`. The reason remained `Human rejection reports adequate resources; verify current resources`. **The new record did not change this advice:** the organizer's earlier rejection already applied. No change is claimed where the output shows none.

## Live records from the app

No feedback was submitted through the UI in this run. This section is reserved for an actual staff review with reviewer, date and outcome.

## What we did not build

The demonstration records are not a human evaluation or a model-training set. Feedback recall is a deterministic lookup over stored records; it is not model retraining or autonomous operational approval.
