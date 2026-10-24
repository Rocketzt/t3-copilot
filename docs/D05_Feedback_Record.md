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

## Live records from the app


## What we did not build

No live application feedback record is reported here before integration and a real app run. Feedback recall is a deterministic lookup over stored records; it is not model retraining or autonomous operational approval.
