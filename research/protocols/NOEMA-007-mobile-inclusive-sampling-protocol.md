# NOEMA-2026-007 — Mobile-inclusive AER sampling pre-registration

- **ID:** NOEMA-2026-007
- **Status:** draft / protocol design only
- **Date:** 2026-11-27
- **Scope:** Georgian municipal or river-basin after-event review, only after a competent authority grants a written mandate
- **Data status:** no event, warning, survey, participant or operational data were accessed

## Research question

How can an after-event review include people who are temporarily present, move between places, work shifts, use transit/service points, or cannot move, without turning a warning-effectiveness study into individual mobility surveillance?

## Evidence and motivation

**FACT:** UNDRR, IFRC, ITU and WMO's *After-Event Review (AER): Methodological guidance on conducting after-event reviews of Early Warning Systems* describes a structured, learning-oriented review of monitoring/prediction, forecasts, warning dissemination, communication, coordination and response. The official page records publication on 15 July 2026 and 76 pages: https://www.undrr.org/publication/documents-and-publications/after-event-review-aer-methodological-guidance-conducting

**FACT:** The joint UNDRR/WMO/IFRC/ITU *Early Warning Systems for mobile populations: Operational guidance* explicitly includes people temporarily present at routes, workplaces and transit hubs, as well as people unable to move because of poverty, disability or insecurity. It says mobility inclusion belongs inside existing multi-hazard early-warning systems rather than a separate system: https://www.undrr.org/publication/documents-and-publications/early-warning-systems-mobile-populations-operational

**INFERENCE:** A resident-only denominator may fail to represent all people exposed during a hazard window. However, a time-location or service-point sample can also omit people who are unable to reach those places. Both coverage and undercoverage must be measured.

**HYPOTHESIS:** A pre-registered combination of stratified time-location sampling and community-partner aggregate summaries may reveal warning comprehension/feasibility gaps not visible in resident-only administrative frames. This has not been tested in Georgia.

## Protocol design

The machine-readable contract is `data/noema-007/aer-sampling-protocol.schema.json`; the semantic validator is `noema_core/aer_sampling.py`.

1. **Mandate and event selection:** require a written mandate from the competent authority. Select only an officially recorded hazard event or a pre-registered exercise. Preserve the official event/warning reference outside this public protocol; do not publish participant or household coordinates.
2. **Separate sampling frames:** keep administrative resident frames, time-location clusters, community-partner aggregates, service-point intercepts and official endpoint aggregates as distinct frames. Do not merge them without an explicit overlap and denominator plan.
3. **Mobility context, not identity:** use only broad context labels such as resident, temporarily present, workplace/shift, transit/service point and mobility-constrained. Do not infer or record nationality, immigration/legal status, persistent device IDs or individual movement histories.
4. **Pre-register inference scope:** convenience, partner-led and service-point samples are descriptive for their frame only. A population estimate is permitted only for a probability design with documented design weights and a defined people denominator. Endpoint counts can never support a people-level population estimate.
5. **Keep value-chain measures separate:** endpoint delivery, survey receipt, comprehension, action feasibility, reported action and verified action have distinct numerator, denominator and unit contracts. An endpoint receipt is not a unique person.
6. **Nonresponse and coverage:** document nonresponse, time-location selection, service-point selection, undercoverage and inaccessible groups. Do not treat people absent from a frame as zero exposure or zero comprehension.
7. **Privacy and release:** no direct identifiers, precise coordinates, device IDs, movement histories, nationality/legal status, raw message content or individual health records in public artifacts. A privacy threshold policy must be approved before any public aggregate release; cross-release differencing review and human privacy review remain mandatory.
8. **Corrective actions:** each accepted finding must be assigned to a competent institutional role and later verified against an observable indicator. NOEMA does not issue official warnings or decide evacuation.

## Measurement contract

| Measure | Numerator | Denominator | Unit | Interpretation |
|---|---|---|---|---|
| Warning delivery | Confirmed endpoints | Attempted endpoints | Endpoints | Channel/endpoint metric only |
| Survey receipt | Respondents reporting receipt | Completed respondents | People | Conditional survey metric |
| Comprehension | Correct comprehension responses | Respondents assessed | People | Survey measure, not delivery |
| Feasibility | Respondents reporting feasible action | Respondents assessed for feasibility | People | Ability to act, not action completion |
| Reported action | Respondents reporting protective action | Respondents assessed for action | People | Self-report, not independently verified |
| Verified action | Respondents with verified action | Respondents assessed for verification | People | Requires a defined, ethical verification method |

## Evidence classification

- **FACT:** the two joint international guidance publications and their stated scope/date are documented on the official UNDRR pages.
- **REPRODUCED RESULT:** synthetic tests validate the schema and reject denominator mixing, endpoint-to-person inference, duplicate frames and non-probability population estimates.
- **INFERENCE:** separate frames and units reduce the risk of silently treating endpoint delivery or resident counts as total people reached.
- **HYPOTHESIS:** the protocol may identify last-mile inclusion gaps in a permissioned Georgian pilot.
- **UNTESTED IDEA:** apply the protocol to a municipality with an approved event-review mandate and independently reviewed aggregate data.

## Limitations

- No Georgian event, warning logs, survey, participant interview, municipal plan or after-action review was accessed.
- Time-location and service-point sampling may under-cover people who cannot move or do not use the sampled sites.
- Partner aggregates may overlap; a trusted overlap plan and disclosure review are required.
- A schema and validator do not prove lawful authority, privacy, representativeness, source authenticity or causal impact.
- No sample sizes, thresholds, local risk rates or effectiveness estimates are asserted.

## Next step

Obtain a written review mandate, agree an event-selection rule and data dictionary, pre-register the sampling frame and weighting plan, and secure independent public-health, accessibility and privacy review before any field collection.
