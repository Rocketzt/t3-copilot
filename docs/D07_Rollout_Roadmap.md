# D07 — Rollout roadmap

> 模拟 / SIMULATED — today’s airports, events and results are fictional organizer data. The stages below are proposed gates for our airline, not a claim of deployment.

**Owner:** Jason · **Status:** Proposed 6–12 month plan for airline review.

Our operations-control duty staff need to know which of **our** airports merits attention first, what to verify, whom to involve and what may be drafted for passengers. The current offline prototype ranks eight simulated airports by detector signals and importance to our airline. Qualified staff retain every flight and communication decision.

| Stage and horizon | Use and accountable roles | Gate to advance |
|---|---|---|
| **Shadow mode, months 0–2** | Our data owner maps and time-stamps real inputs; operations analysts compare silent rankings and drafts with their established workflow; a safety reviewer records errors. No draft is operationally used. | **Zero invented numbers** in an audited sample; all numeric claims trace to current source records. The offline exam remains **21/21** on its fixed simulated set, and new airline cases are documented separately. Reviewer signs off on source mapping and stop conditions. |
| **Assisted use, months 3–6** | Duty staff may consult the view and edit drafts. The operations lead approves escalation; passenger-service lead approves any outward message. Data owner watches missing and conflicting sources. | **Zero invented numbers** in reviewed outputs; the fixed exam continues to pass **21/21** and airline-specific must/must-not cases pass at an agreed threshold; named operations and passenger reviewers sign off before any assisted use expands. |
| **Monitored use, months 7–12** | Our operations lead owns decisions and incident response; data owner monitors freshness and drift; model owner reviews append-only Accept/Edit/Reject feedback and checker failures. | Continue only while audited outputs have **zero invented numbers**, the exam gate stays met, and periodic reviewer sign-off is current. Any PII leak, unsourced claim or unauthorized action pauses the tool for investigation. |

The **21/21** score is the result of the current simulated offline exam, not a real airline acceptance score. Human tone and action-order ratings remain to be collected; their sign-off is a future gate, not a completed milestone.

## Data our airline would need to provide

We would need an approved flight schedule and formal status feed; aircraft rotations; crew assignments; gate and ground-support state; airport and weather updates with source, definitions and timestamps; our own airport and route importance; and approved message templates and reviewer identities. Access rules, retention limits and privacy controls must be agreed before those feeds enter the system.

## Future scope from our airline’s point of view

With those real inputs, we could evaluate flight and route impact and later add fleet and multiple-base views. The present network ranking is a triage cue from monthly airport data; it cannot make a flight-level judgment.

## What we did not build

We have no production data integration, flight-level model, autonomous dispatch, official passenger sending, live monitoring service or validated real-world error rate. These stages require airline data access and reviewer approval before implementation.
