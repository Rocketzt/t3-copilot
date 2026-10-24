# D06 — Risk card

> 模拟 / SIMULATED — fictional organizer data and events. This is a proposed control card for our airline's disruption desk, not a live safety certification.

**Owner:** Jason · **Status:** Draft for airline review. Evidence: the fresh offline exam passed 21/21, including its fabricated-number negative case; the unit suite passed 41 tests.

| Failure mode | Signal we would watch | Impact on our airline | Likelihood from current evidence | Mitigation and owner |
|---|---|---|---|---|
| The writer invents a number | A numeric claim is absent from `facts.numbers`; checker C02 fails. The bad-writer example inserts “20 points” into f05. | Staff could act on an unsupported comparison. | Demonstrated as a deliberate failure in bad mode; live frequency is unmeasured. | Block the output, show the offending field and require a sourced correction. The negative exam case passed. Our output reviewer checks any corrected draft. |
| Monthly data are mistaken for flight-level status | An answer names a flight, aircraft, crew member or gate from an airport-month average. | A passenger or dispatcher may infer a delay or action that has not been confirmed. | Structural risk: the simulated source has no flight-level records. | Label the period and source, state the missing current information, and require our operations staff to check live airline and airport systems before acting. |
| Weather is missing or sources conflict | Weather row is marked missing, or event sources disagree. EVT003 returns `Can't tell`. | A firm risk label or causal story would hide uncertainty. | Present in the test scenarios; live frequency is unknown. | Do not impute weather or choose a convenient source. Show the gap, verify update times and definitions, and escalate to the operations lead. |
| Staff over-trust an automated draft | A user treats a draft as an instruction or skips its checker, source and review status. | Unauthorized cancellation, release, dispatch, maintenance, compensation or passenger communication. | Unmeasured until human trials. | Keep decisions with qualified staff (RULE007), mark passenger text as a draft, require sign-off, and retain Accept/Edit/Reject feedback without overwriting earlier records. |

## When we would stop using it

Pause use for any checker failure, PII leak, missing provenance, unhandled source conflict, or answer that implies a flight decision was made. Suspend assisted use if an airline reviewer cannot verify the current aircraft, crew, gate and formal flight status. Resume only after the responsible owner checks the source and a qualified person signs off.

## What we did not build

We have no live airline feeds, flight-level validation, measured deployment error rates, automatic operational authority or automatic passenger sending. The 21/21 exam covers specified simulated cases; it does not establish real-world reliability.
