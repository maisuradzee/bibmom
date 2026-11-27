# NOEMA-007 — Global MHEWS status 2026: system presence is not person-level protection

**Research ID:** NOEMA-2026-007  
**Date:** 2026-11-27  
**Status:** Draft  
**Pillars:** DISCOVERY · RESEARCH · INNOVATION

## Research question

How should NOEMA-007 interpret global early-warning progress without conflating national system existence, four-pillar capability, population reach, timely receipt, comprehension, feasible action and verified protective outcomes?

## Primary-source facts

### FACT — WMO Global Status of MHEWS 2026

WMO's publication page, dated 2026-11-11, reports:
- 136 countries reporting multi-hazard early warning systems as of August 2026;
- a 143% increase in countries reporting MHEWS since 2015;
- a headline that 70% of countries report having MHEWS;
- fewer than half of reporting countries demonstrate capabilities across all four pillars;
- more comprehensive systems are associated with lower disaster mortality and fewer people affected.

Primary source: https://wmo.int/resources/publication-series/global-status-of-multi-hazard-early-warning-systems/gsmhews-2026

The snapshot preserves these as source-reported facts. It does not reconstruct a 2015 baseline, infer an exact country denominator from the rounded 70% headline, or derive a causal mortality effect.

### FACT — mobile-population operational guidance

The 2026 UNDRR/WMO/IFRC/ITU operational guidance identifies people temporarily present along routes, at workplaces or transit hubs, as well as people unable to move because of poverty, disability or insecurity. It frames mobility as a persistent risk characteristic rather than a separate warning system.

Primary source: https://www.undrr.org/publication/documents-and-publications/early-warning-systems-mobile-populations-operational

## Evidence interpretation

**INFERENCE:** a national MHEWS indicator is a system-level measure. It cannot be substituted for the proportion of people exposed to a hazard who received a specific warning in time, understood it, could act, or completed a verified protective action.

**INFERENCE:** four-pillar capability and last-mile outcomes are distinct measurement layers. They should not be combined into a single score unless the unit, denominator, time window and weighting are explicit and justified.

**HYPOTHESIS:** an event-linked measurement ledger that records each stage with its own denominator and evidence provenance will reduce false claims of warning coverage and action effectiveness.

**UNTESTED IDEA:** a future local evaluation could combine coarse, authority-approved hazard-area/time windows with probability-based surveys and separately audited endpoint delivery receipts. This requires an authorized event-review mandate and independent privacy review.

## NOEMA-007 design consequences

Keep the following units and stages separate:
1. country-level existence of an MHEWS;
2. country-level capability across the four pillars;
3. hazard-area and time-window exposure frame;
4. technical endpoint delivery;
5. respondent-reported timely receipt;
6. warning comprehension;
7. practical ability to act;
8. self-reported protective action;
9. independently verified action and outcomes.

A message endpoint is not a person. A person count is not a warning-event denominator. A respondent's recall is not timestamp-verified receipt. An association between system comprehensiveness and outcomes is not a causal effect estimate.

## Method and reproducibility

- Source extraction only from the two linked official publication pages.
- Values are preserved verbatim as source-reported statements in the global MHEWS snapshot JSON.
- No new arithmetic is performed; derived_results is intentionally empty.
- The JSON Schema and synthetic tests check denominator semantics, inequality direction, global-only scope and the absence of a causal claim.

## Limitations and safety

- This is global context, not a Georgia country assessment.
- The WMO summary page does not expose the underlying country-level dataset in the retrieved page; no country-level table was reconstructed.
- The 70% headline is rounded and no denominator is inferred.
- The outcome relationship is recorded as association, not causation.
- No personal, device, message, location, event or survey data is included.
- No new warning service or automated alerting is implemented.

## Next step

For Georgia, obtain an authorized country-level MHEWS assessment and event-review mandate. Pre-register hazard/event inclusion, population frames (resident, temporary presence, service-point and people unable to move), sampling weights, timing definitions, missingness rules and independent verification before any local effectiveness estimate.

## Sources

- World Meteorological Organization. (2026-11-11). *Global Status of Multi-Hazard Early Warning Systems 2026*. https://wmo.int/resources/publication-series/global-status-of-multi-hazard-early-warning-systems/gsmhews-2026
- UNDRR, WMO, IFRC and ITU. (2026). *Early Warning Systems for mobile populations: Operational guidance*. https://www.undrr.org/publication/documents-and-publications/early-warning-systems-mobile-populations-operational
