# NOEMA-007 — Warning-to-Action Readiness Architecture

- **Version:** 0.1
- **Date:** 2026-11-28
- **Status:** Preliminary engineering design; not deployed
- **Portfolio stream:** NOEMA-2026-007

## Purpose

Move NOEMA-007 from a warning-delivery-only view toward a privacy-preserving, denominator-explicit warning-to-action model. The design distinguishes warning issue, transmission, delivery, human receipt, comprehension, action feasibility, self-reported action, independent verification and outcome.

The goal is not to score or blame households. It is to identify system bottlenecks such as inaccessible messages, language barriers, lack of transport, unsafe routes, unavailable shelter, insufficient lead time or low trust.

## Evidence and interpretation

The Lloyd's Register Foundation report From alert to agency was published 2026-10-13 using the publisher's 2025 Wave 4 World Risk Poll dataset. NOEMA pinned the public Parquet source by repository commit, Git blob SHA-1, byte length and SHA-256 and independently reproduced selected weighted aggregates.

- Warning receipt: 80.0%.
- Self-reported ability to act among warned respondents: 63.8%.
- Ability to act by one, two and three warning channels: 37.5%, 50.5%, 64.2%.
- Ability to act by plan/agency group: neither 26.6%; plan only 49.5%; agency only 60.0%; both 83.0%.
- Ability to act by publisher income groups: 48.0%, 46.9%, 75.5%, 70.9%.

These are weighted, cross-sectional, retrospective self-reports: descriptive associations, not causal effects. They do not verify warning timestamps, individual receipt, comprehension, actual action or avoided loss. No design-based confidence intervals were reproduced. Georgia's warning-question base is 99, below the publisher's n>=100 country-ranking threshold; NOEMA makes no Georgia national effectiveness estimate.

## Two separate evidence lanes

### Lane A — Population survey context

Use for weighted population-level context and subgroup associations. Store dataset version/digests, wave, population, sampling/weighting design, denominators, estimates, uncertainty where available, and self-report limitations. WRP aggregates remain in this lane. Do not load WRP respondents into the event-level schema or treat country subgroup percentages as operational event metrics.

### Lane B — Operational event aggregates

Use for a specific, officially documented hazard-warning event and privacy-approved aggregates. The existing noema_core/action_readiness.py and data/noema-007/action-readiness-observation.schema.json are a preliminary event-level aggregate contract, not a live alerting service. It does not ingest raw delivery logs. It separates:
- attempted message endpoints from confirmed endpoints; endpoint counts are not people;
- event-specific survey receipt from message comprehension;
- action feasibility from self-reported protective action;
- self-reported action from independently verified action.

Never combine Lane A and Lane B numerators or denominators. Do not use global survey percentages as local event baselines or infer that a channel-count association is the causal effect of adding a channel.

## Proposed warning-to-action stages

1. Risk/forecast: hazard, area and time window from an authoritative source.
2. Authorized warning issued: competent authority approval and non-personal public reference.
3. Transmission attempted: endpoint counts by channel and event window.
4. Delivery confirmed: endpoint counts, never labelled as people reached.
5. Human receipt measured: explicit survey or validated method.
6. Comprehension assessed: assessed denominator and correct-understanding numerator.
7. Action feasibility assessed: whether a safe, realistic protective option existed.
8. Protective action self-reported: explicit asked denominator and numerator.
9. Protective action independently verified: only with a defined independent method.
10. Outcome assessed: definition, observation window, source and uncertainty.

Missing stages remain unknown/null, not zero. A warning not observed in a source is not automatically a warning that was not issued.

## Data contract and denominator rules

Use the existing event-level schema as the starting point: random non-personal event ID, hazard class, coarse official area code, warning authority/reference/source, canonical UTC timestamps, measurement window, channel, attempted and confirmed endpoint counts, optional event-specific survey counts, privacy approvals, evidence sources and limitations.

Every rate must include numerator, denominator, denominator unit, observation window and missingness rule. Keep endpoint denominators separate from respondent denominators. Keep survey frame, invited, completed, received, assessed, feasible, reported and verified counts separate.

The current validator requires a minimum cell-size floor of 10 and data-controller/privacy-reviewer approval. This is a NOEMA release-policy floor, not a statutory safe harbour; threat modelling may require a higher threshold, coarser geography or suppression entirely.

## Privacy and human-rights safeguards

- No names, phone numbers, personal IDs, household addresses, exact household coordinates, raw message text or raw device logs in public records.
- Use coarse official area codes and random event identifiers.
- Require controller approval, privacy review, source provenance and a retention policy before operational data is accepted.
- Do not create individual risk scores or infer personal income/health status from area-level data.
- Do not publish municipality rankings from small or non-representative samples.
- Review small-cell and differencing/re-identification risk across repeated releases.
- Separate warning receipt from ability to act; lack of transport, shelter, accessible routes or a safe destination is a system constraint, not a personal failure.
- Do not let a missing survey or log become a zero-performance value.

## Failure modes and competing explanations

- A confirmed SMS endpoint does not prove a person read the message.
- More channels may correlate with better-resourced areas; the survey does not identify the causal effect of redundancy.
- Household plans may correlate with resources, safer housing or prior hazard experience.
- Non-response, recall error and social-desirability bias affect self-report.
- False alarms, warning fatigue, network/power failure, inaccessible language/format, unsafe routes and insufficient shelter can break the chain after delivery.
- Event severity, lead time and exposure differ; raw percentages should not be compared across events without adjustment and uncertainty analysis.

## Validation plan

Before a Georgian pilot: obtain documented authority for official warning logs and post-event aggregates; predefine event frame, measurement window, stages and denominators; obtain survey design/weights and variance method; validate timestamps and endpoint semantics; test missing-stage handling, small-cell suppression and source provenance; obtain independent privacy/method review; compare self-report with independent verification where lawful; publish uncertainty and limitations.

## Success measures

- Every stage has an explicit numerator, denominator, unit and observation window.
- Delivery endpoints are never reported as people reached.
- Receipt, comprehension, feasibility, self-reported action and verified action remain separate.
- No personal or raw device-level data enter the public repository.
- Missing stages remain unknown rather than being imputed as zero.
- Any local effectiveness claim has a documented sampling design, uncertainty estimate and independent review.

## Current limitations and next steps

No privacy-approved Georgian event-level warning log, post-event survey or independent outcome dataset was accessed in Run 47. WRP is global context, not a substitute for local evidence. The current module is a validation/metrics prototype, not a deployed operational service.

Next: obtain authorized NEA/civil-protection event aggregates, define a small pilot with a competent data controller, keep public artifacts aggregate-only and obtain independent review before field use.

## Sources

- Lloyd's Register Foundation, From alert to agency: What turns warnings into action? (2026-10-13), DOI 10.60743/yx1k-t541. [Report](https://www.lrfoundation.org.uk/sites/default/files/2026-10/world-risk-poll-report-2026-early-warnings.pdf).
- Lloyd's Register Foundation, WRP 2025 Wave 4 public data and publisher reproduction code/results, pinned commit f2b810c3c4333de6347ad2c9eade3c48ae17be4c. [Dataset repository](https://github.com/lrfoundation/world_risk_poll_data/tree/f2b810c3c4333de6347ad2c9eade3c48ae17be4c).
- United Nations Office for Disaster Risk Reduction, Bridging the early warning-to-action gap requires building resilience at home (2026-10-13). [UNDRR summary](https://www.undrr.org/implementing-sendai-framework/bridging-the-early-warning-to-action-gap-requires-building-resilience-at-home).
- NOEMA event-level prototype: noema_core/action_readiness.py; schema: data/noema-007/action-readiness-observation.schema.json; tests: tests/test_noema007_action_readiness.py.
