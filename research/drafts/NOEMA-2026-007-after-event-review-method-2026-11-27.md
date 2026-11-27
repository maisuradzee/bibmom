# NOEMA-2026-007 — After-Event Review protocol for mobile-inclusive early warnings

- **Date:** 2026-11-27
- **Status:** documentary research and synthetic schema prototype; no Georgian event review or field pilot has been conducted
- **Related stream:** NOEMA-2026-007 Last-Mile Action Gap
- **Evidence boundary:** primary international operational guidance; no local operational data

## Research question

How can a post-event review distinguish failures in risk knowledge, monitoring/forecasting, warning decisions, dissemination, receipt, comprehension, preparedness and response, while explicitly considering people whose presence or ability to act changes over time?

## Primary-source findings

1. UNDRR, IFRC, ITU and WMO published the *After-Event Review (AER): Methodological guidance on conducting after-event reviews of Early Warning Systems* on 15 July 2026. The official publication page describes a structured review of monitoring and prediction, forecasts, warning dissemination, communication, coordination and response. It emphasizes a learning-oriented, non-punitive review and improvements across the four MHEWS pillars. The PDF is 76 pages. Source: https://www.undrr.org/publication/documents-and-publications/after-event-review-aer-methodological-guidance-conducting
2. UNDRR, WMO, IFRC and ITU published *Early Warning Systems for mobile populations: Operational guidance* on 15 July 2026. It addresses people affected by changing locations or circumstances and treats mobility inclusion as part of the existing multi-hazard system, not a separate warning system. Source: https://www.undrr.org/publication/documents-and-publications/early-warning-systems-mobile-populations-operational

The AER publication page is primary evidence for the guidance's stated scope and principles. This note does not claim to have independently reviewed every page of the downloadable 76-page PDF.

## Proposed review sequence

1. **Define the event and review mandate.** Use an official event/warning reference, a coarse official area code and a UTC event window. Do not include coordinates of homes, shelters or individuals.
2. **Reconstruct the expected chain.** Record the responsible authority, forecast/monitoring basis, warning decision, issue time, action deadline, official channels and preparedness arrangements from source documents.
3. **Reconstruct the observed chain.** Separate issued warnings, attempted endpoints, confirmed endpoint receipts, voluntary survey receipt, comprehension, action feasibility, reported action and independently verified action. Endpoint counts are not unique people.
4. **Include mobility without profiling.** Where a locally justified review requires it, use time-and-place sampling frames or community-partner summaries. Do not infer or record nationality, legal/migration status, persistent device identifiers or individual movement histories.
5. **Triangulate evidence.** Keep primary records, aggregate operational data, aggregate survey results and interview summaries distinguishable. Mark every conclusion FACT, REPRODUCED_RESULT, INFERENCE, HYPOTHESIS or UNTESTED_IDEA.
6. **Agree recommendations.** Assign each action to an institutional role, with a due date and an observable verification indicator. Review progress in a later exercise or event.
7. **Publish only reviewed aggregates.** The schema rejects direct identifier and raw-log fields, but cannot detect personal data embedded in free text. Human privacy review and cross-release disclosure controls remain mandatory.

## Prototype

`data/noema-007/aer-finding-register.schema.json` defines a closed, metadata-only finding register. It requires:
- one event reference and coarse area/time scope;
- explicit MHEWS pillar and warning-value-chain stage;
- evidence class and source references;
- limitations and an actionable recommendation;
- a public-safe data classification and explicit no-identifiers/no-raw-logs declarations.

The schema is a structural guard only. Self-declared privacy booleans are not proof of privacy, approval, authenticity or lawful authority. The test fixture is synthetic and is not an actual Georgian event review. Free-text fields still require human review.

## Evidence classification

- **FACT:** the two UNDRR-led publications exist, are dated 15 July 2026, and their official pages describe the scope summarized above.
- **REPRODUCED_RESULT:** synthetic JSON-schema tests accept a complete safe fixture and reject unapproved fields, direct-identifier declarations and unsupported evidence classes.
- **INFERENCE:** a structured, non-punitive after-event review can connect NOEMA-007's existing delivery/receipt/comprehension/feasibility/action metrics to accountable institutional improvements.
- **HYPOTHESIS:** including time-and-place or partner-led sampling in a Georgian pilot may reveal warning gaps not visible in resident-only denominators.
- **UNTESTED_IDEA:** a local pilot with a Georgian municipality, warning authority, community organizations and independently reviewed aggregate data.

## Limits and next step

No official Georgian event dataset, after-action review, municipal plan, survey or participant interview was accessed. No operational warning was issued or evaluated. The schema does not authenticate reviewers, enforce event chronology, detect free-text personal data, prevent cross-release differencing or establish causal impact.

Next step: obtain a municipality/agency-approved event-review mandate and data dictionary; preregister the event selection, denominators, sampling and privacy controls before any field collection. Keep the prototype documentary until that authorization exists.
