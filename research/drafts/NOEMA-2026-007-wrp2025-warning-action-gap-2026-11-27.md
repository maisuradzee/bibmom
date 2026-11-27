# NOEMA-2026-007 — WRP 2025 warning receipt and action-feasibility gap

- **ID:** NOEMA-2026-007-WRP2025-WARNING-ACTION-001
- **სტატუსი:** draft / source-grounded discovery
- **თარიღი:** 2026-11-27
- **სფერო:** multi-hazard early warning · last-mile protective action
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

What does the World Risk Poll 2025 evidence say about the gap between receiving a warning and being able to act, and what can legitimately be inferred about Georgia from the published sample base?

## მოკლე შეჯამება

The Lloyd's Register Foundation's 2026 report From alert to agency reports that 80% of impacted respondents who were asked about warning channels received at least one warning, while 35.8% of warned respondents were not able to act (published as 36%). The report's public reproduction identifies 24,249 respondents in the warning-question base and 16,996 warned respondents in the ability-to-act base.

Georgia had 101 respondents reporting disaster impact but only 99 in the warning-question base. The report uses a minimum base of 100 respondents asked about warnings for country rankings, so Georgia is excluded. These survey results are not a national operational audit, event-level delivery log, or causal estimate of warning effectiveness.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

A warning is only one stage in a protective-action chain. A person may not receive a message, may receive it too late, may not understand it, may lack transport or safe shelter, may be unable to leave work or care responsibilities, or may receive advice that is not feasible in the local context.

Treating warning receipt as success hides these different failure modes. NOEMA-007 therefore separates system capability, warning issuance, delivery, receipt, comprehension, feasibility, completed protective action and avoided loss.

## არსებული ცოდნა და წყაროები

1. Lloyd's Register Foundation, From alert to agency: What turns warnings into action?, World Risk Poll 2026 report, DOI: https://doi.org/10.60743/yx1k-t541. The report gives the global warning-receipt and action-feasibility findings and the Georgia sample-base threshold.
2. Lloyd's Register Foundation, World Risk Poll Data, WRP 2025 Wave 4: https://github.com/lrfoundation/world_risk_poll_data/tree/main/WRP_2025. The public release contains 143,459 respondents from 140 countries/territories, uses PROJWT for pooled estimates and is licensed CC BY-SA 4.0.
3. Lloyd's Register Foundation, report reproduction and method notes: https://github.com/lrfoundation/world_risk_poll_data/tree/main/reports/WRP_2025/core_from_alert_to_agency. The source reproduction identifies 24,249 in the warning-question base, 16,996 warned respondents in the action question, 80.0% receipt, 63.8% able and 35.8% unable. This is the publisher's reproduction, not an independent NOEMA reproduction.
4. World Meteorological Organization and Early Warnings for All partners, Early Warnings for All: Toolkit for Monitoring & Evaluation, version 1.0, August 2024: https://wmo.int/sites/default/files/2024-09/EW4ALL%20ME%20Toolkit_Final%20Version%201_August2024.pdf. It supports separating capability, reach, response and effectiveness indicators.
5. Xu, H., Lu, Y., Chen, Y. et al. (2026). “Warning response behavior model: conceptual clarification and operationalization.” Natural Hazards, 122, article 200. DOI: https://doi.org/10.1007/s11069-026-08003-1. The paper reviews warning-response concepts and distinguishes information processing, cognitive evaluation and intention-to-action conversion.
6. Graf, J., Renner, R., & Klebel, T. (2026). “Bridging warning and adaptation addressing risk communication strategies for short-term natural hazard warnings and long-term risk adaptation – A scoping review.” Progress in Disaster Science, 29, 100515. DOI: https://doi.org/10.1016/j.pdisas.2026.100515. The review maps 194 peer-reviewed studies across time horizons, hazard groups and communication purposes.
7. Visser, H., de Bruin, S. P., Bouwer, L. M., & Petersen, A. C. (2026). “Temporal characteristics of disaster data: how to avoid misconceptions, misinterpretation or misuse.” International Journal of Disaster Risk Reduction, 142, 106188. DOI: https://doi.org/10.1016/j.ijdrr.2026.106188. Used as a caution against misreading time-varying disaster datasets.

## მტკიცებულებები

- **FACT:** The WRP 2025 public wave contains 143,459 respondents from 140 countries/territories; the public dataset is CC BY-SA 4.0.
- **FACT:** The source report defines the warning base as impacted respondents who named a disaster type; it reports 24,249 in this base and 16,996 warned respondents asked about ability to act.
- **FACT:** The source report reports 80.0% receiving at least one warning among the warning-question base, 63.8% able to act and 35.8% unable to act among the action-question base.
- **FACT:** Georgia has 101 impacted respondents but 99 in the warning-question base; the report's country ranking requires at least 100 respondents asked about warnings.
- **SOURCE-PUBLISHED REPRODUCTION:** The publisher's Python/R scripts and RESULTS file reproduce the reported aggregates. NOEMA has not independently rerun the raw Parquet calculation in this note.
- **INFERENCE:** The difference between receipt and ability to act indicates that reach alone is an incomplete performance measure; it does not identify the cause of the action gap.
- **HYPOTHESIS:** Linking permissioned event-level warning records with after-action data and local feasibility observations will identify actionable bottlenecks more reliably than a single national capability score.
- **UNTESTED IDEA:** An aggregate-only action-readiness dashboard could display the funnel from issuance to verified action while suppressing small cells and keeping each denominator explicit.

## კონკურენტი ახსნები

Inability to act may result from late receipt, unclear content, low trust, inaccessible formats, transport constraints, unsafe routes, disability-related barriers, household care duties, livelihood constraints, insufficient shelter, or a warning that did not require the respondent to act. Survey recall and interpretation may also affect answers. The aggregate report cannot distinguish these mechanisms.

## ჰიპოთეზა

If every stage of the warning-to-action chain is measured with its own denominator and linked to authorised event-level after-action evidence, NOEMA-007 can distinguish communication failures from practical constraints and help institutions target interventions without claiming causal effects from cross-sectional survey data.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Pin the public WRP 2025 Parquet source to an immutable upstream commit and Git blob; compute SHA-256 before analysis.
2. Use PROJWT for pooled global estimates and follow the source report's exact response-code and denominator rules.
3. Reproduce the 24,249 and 16,996 bases before comparing rounded 80.0%, 63.8% and 35.8% values.
4. Recompute Georgia's impacted and warning-question bases; preserve the 99-person threshold exclusion.
5. Keep survey rows local to the temporary analysis environment; retain only aggregate results, source hashes and method metadata.
6. For local validation, request authorised aggregates for warning issue time, channel delivery, acknowledgement, comprehension, feasible action and verified protective action, keyed by event and broad area.
7. Pre-register privacy thresholds and missing-data handling before any local analysis.

## შედეგები და ინტერპრეტაცია

The published source result is a warning-receipt rate of 80.0% and an inability-to-act rate of 35.8% among warned respondents asked the action question. These are different denominators and must not be subtracted or treated as a single population funnel without individual-level linkage.

Georgia's 99-person warning-question base is below the report's 100-person ranking threshold. The sample is not sufficient to support a robust national warning-effectiveness claim. A local administrative dataset is needed.

## შეზღუდვები და გაურკვევლობები

- The survey is retrospective self-report, not an operational warning-event log.
- No confidence intervals or survey-design variance are recomputed in this note.
- The 2025 China sample is an opt-in web panel.
- Georgia's warning-question base is 99; it is not a robust national estimate.
- Warning receipt does not prove comprehension, action feasibility, completed action or avoided loss.
- The source publisher's reproduction is not an independent NOEMA reproduction.
- No Georgian municipal event-level delivery or after-action dataset has been ingested.
- No private location, household, health or respondent-level data is included.

## დასკვნა

The most important research finding is the measurement gap between warning receipt and ability to act. NOEMA-007 should not score a warning system as effective solely because a message was sent or received. The next evidence step is a permissioned, event-linked Georgian dataset with separate delivery, comprehension, feasibility and action denominators.

## წყაროები

- https://doi.org/10.60743/yx1k-t541
- https://github.com/lrfoundation/world_risk_poll_data/tree/main/WRP_2025
- https://github.com/lrfoundation/world_risk_poll_data/tree/main/reports/WRP_2025/core_from_alert_to_agency
- https://wmo.int/sites/default/files/2024-09/EW4ALL%20ME%20Toolkit_Final%20Version%201_August2024.pdf
- https://doi.org/10.1007/s11069-026-08003-1
- https://doi.org/10.1016/j.pdisas.2026.100515
- https://doi.org/10.1016/j.ijdrr.2026.106188

## შემდეგი ნაბიჯები

1. Independently reproduce the selected WRP 2025 aggregates from the pinned public Parquet file.
2. Obtain authorised Georgian warning-event and after-action aggregates with explicit event and area denominators.
3. Design a local last-mile study that separately measures receipt, comprehension, feasibility, intended action and verified protective action.
4. Obtain independent survey-methodology, DRR and privacy review before operational use.

## შემოწმების სტატუსი

- Primary report, public data dictionary and publisher reproduction reviewed: complete.
- Peer-reviewed warning-response sources checked: complete.
- Independent NOEMA reproduction: pending.
- Georgian event-level validation: blocked by authorised data access.
- Independent external review: not performed.
- Publication status: draft only.

## ცვლილებების ისტორია

- 2026-11-27: initial source-grounded discovery note; no respondent-level or private data added.
