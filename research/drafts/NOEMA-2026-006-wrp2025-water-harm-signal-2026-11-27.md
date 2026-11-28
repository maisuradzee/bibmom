# NOEMA-2026-006 — Global self-reported drinking-water harm signal

- **ID:** NOEMA-2026-006-WRP2025-WATER-HARM-001
- **სტატუსი:** draft / discovery evidence
- **თარიღი:** 2026-11-27
- **სფერო:** drinking-water safety · public-health signal discovery
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow

## საკვლევი კითხვა

What can the 2025 World Risk Poll self-reported drinking-water harm indicator tell AquaSignal about the scale of a possible human need, and what additional evidence is required before it can be interpreted as measured water contamination or a local Georgian risk estimate?

## მოკლე შეჯამება

The Lloyd's Register Foundation's 2026 report The quiet hazards reports that 13% of adults globally personally experienced serious harm associated with drinking water in the preceding two years, its highest reported level since the poll began. This is a discovery signal, not a laboratory measurement, regulatory compliance result, diagnosis, or causal attribution to a specific water source.

The public WRP 2025 dataset contains 143,459 respondents from 140 countries and territories and is licensed CC BY-SA 4.0. Its drinking-water harm variable is WP22443. The report defines personally experienced harm as the sum of “yes, personally experienced” and “both” responses, and its method note says those rounded percentages are summed. The publisher's own reproduction reports 13%. NOEMA has not independently rerun the underlying respondent-level calculation in this note.

## რატომ არის ეს კითხვა მნიშვნელოვანი?

A self-reported health signal can reveal a possible unmet need even where routine water-quality monitoring is sparse. However, self-report and measured water quality answer different questions. AquaSignal must not convert reported harm into a contamination alert without independent sample-level evidence and public-health review.

The signal is useful for deciding where to seek better data: monitoring-station histories, drinking-water compliance records, laboratory results, service interruptions and health surveillance. It does not identify which source, contaminant, exposure route or time period caused any respondent's reported harm.

## არსებული ცოდნა და წყაროები

1. Lloyd's Register Foundation, The quiet hazards: How everyday risk shapes daily life, World Risk Poll 2026 report, 23 June 2026, DOI: https://doi.org/10.60743/9djc-t718. Supports the published global drinking-water harm result and its definition.
2. Lloyd's Register Foundation, World Risk Poll Data, WRP 2025 Wave 4: https://github.com/lrfoundation/world_risk_poll_data/tree/main/WRP_2025. The release contains 143,459 respondents in 140 countries/territories; pooled estimates use PROJWT; licence CC BY-SA 4.0.
3. WRP 2025 report reproduction, The quiet hazards: https://github.com/lrfoundation/world_risk_poll_data/tree/main/reports/WRP_2025/core_the_quiet_hazards. The publisher's RESULTS file records 13% for the drinking-water personal-harm finding. This is the publisher's reproduction, not a NOEMA reproduction.
4. WRP 2025 data dictionary, variable WP22443: “Experienced Harm in Past Two Years: Drinking Water (You/Someone You Know)”; codes 1 = yes, personally experienced; 2 = know someone; 3 = both; 4 = no; 98/99 = don't know/refused: https://github.com/lrfoundation/world_risk_poll_data/blob/main/WRP_2025/WRP_2025_data_dictionary.csv
5. Wright, J., Gundry, S., & Conroy, R. (2004). “Household drinking water in developing countries: a systematic review of microbiological contamination between source and point-of-use.” Tropical Medicine & International Health, 9(1), 106–117. DOI: https://doi.org/10.1046/j.1365-3156.2003.01160.x. Meta-analysis of 57 studies; bacteriological quality can decline between collection and household use, with setting-specific variation.
6. Brown, J. et al. (2025). “Systematic Review of the Microbiological Performance of Household Water Treatment Technologies.” Environmental Science & Technology, 59(41), 21776–21789. DOI: https://doi.org/10.1021/acs.est.4c03494. This evaluates treatment performance, not the WRP self-report measure.
7. WHO, Guidelines for Drinking-water Quality: https://www.who.int/teams/environment-climate-change-and-health/water-sanitation-and-health/water-safety-and-quality/drinking-water-quality-guidelines. Reference framework for future laboratory and compliance interpretation.

## მტკიცებულებები

- **FACT:** WRP 2025 has 143,459 respondents and 140 countries/territories; the public dataset is CC BY-SA 4.0.
- **FACT:** WP22443 records serious harm in the past two years associated with drinking water and distinguishes personal experience, knowing someone, both, no, and DK/refused.
- **FACT:** The report's published global value is 13% for personally experienced harm, defined as codes 1 and 3 using its rounded-sum rule.
- **SOURCE-PUBLISHED REPRODUCTION:** The publisher's Python/R reproduction records 13%. NOEMA has not independently rerun the Parquet calculation.
- **INFERENCE:** The result justifies investigation of water-safety evidence gaps but cannot identify a contaminant, source, location or regulatory exceedance.
- **HYPOTHESIS:** Combining authorised water-quality time series, laboratory results, service interruption records and aggregated health signals may help AquaSignal identify where confirmatory sampling has the greatest value.
- **UNTESTED IDEA:** Use a privacy-preserving anomaly triage layer to prioritise confirmatory sampling; do not issue public safety alerts without competent-authority confirmation.

## კონკურენტი ახსნები

Reported harm may reflect microbiological contamination, chemical exposure, intermittent supply, unsafe storage/handling, non-water causes attributed by respondents to drinking water, recall error or different interpretations of the question. The survey alone cannot distinguish these explanations.

## ჰიპოთეზა

If self-reported signals are kept separate from measured water-quality observations and linked only through permissioned, time- and geography-aligned aggregate evidence, AquaSignal may help identify where independent sampling and public-health investigation are most useful without overstating causality.

## მეთოდი ან ექსპერიმენტის გეგმა

1. Preserve the source report, method note, WRP data dictionary and licence as separate source records.
2. For a future independent reproduction, pin the exact upstream commit and Parquet Git blob; compute and retain SHA-256.
3. Use PROJWT for pooled global calculations; retain DK/refused in the report-defined denominator.
4. Reproduce codes 1 and 3 separately and apply the report's rounded-sum rule; retain the unrounded combined proportion as a diagnostic.
5. Do not commit respondent-level records, random respondent IDs, household coordinates or raw survey rows.
6. Compare the self-reported signal with authorised, quality-controlled laboratory and monitoring data only after legal, privacy and method review.

## შედეგები და ინტერპრეტაცია

The source-published result is 13%. It is a global weighted retrospective self-report indicator for 2025, not a Georgia-specific prevalence estimate and not a measured contamination rate. The publisher's reproduction is available; an independent NOEMA reproduction remains outstanding.

The peer-reviewed source-to-point-of-use review supports the separate principle that source-water quality alone may not describe water quality after collection, storage and handling. It does not establish that this mechanism explains the WRP result or any Georgian case.

## შეზღუდვები და გაურკვევლობები

- The poll provides no water sample, contaminant concentration, regulatory threshold, clinical diagnosis or causal link to a named source.
- No survey-design variance or confidence interval is recalculated.
- The WRP 2025 China sample is an opt-in web panel; modes and country coverage differ.
- The global result must not be projected onto Georgia or a municipality.
- The publisher's reproduction is not an independent NOEMA reproduction.
- No NEA RAR payload, NEA122 sample-level export, NFA compliance dataset or local laboratory time series has been ingested.
- No personal, household, health, private-well-owner or precise private-location data is included.

## დასკვნა

The 13% self-reported result is a high-value discovery signal, not a water-quality finding. AquaSignal should use it to justify evidence acquisition and targeted validation while keeping survey reports, laboratory observations, regulatory compliance and health outcomes as separate evidence classes.

## წყაროები

- https://doi.org/10.60743/9djc-t718
- https://github.com/lrfoundation/world_risk_poll_data/tree/main/WRP_2025
- https://github.com/lrfoundation/world_risk_poll_data/tree/main/reports/WRP_2025/core_the_quiet_hazards
- https://doi.org/10.1046/j.1365-3156.2003.01160.x
- https://doi.org/10.1021/acs.est.4c03494
- https://www.who.int/teams/environment-climate-change-and-health/water-sanitation-and-health/water-safety-and-quality/drinking-water-quality-guidelines

## შემდეგი ნაბიჯები

1. Independently reproduce the WRP 2025 WP22443 aggregate from the pinned public dataset; retain only aggregate results and source hashes.
2. Obtain the NEA 2021–2025 RAR through an official authorised transfer route; verify payload hash, methods, station/sample definitions and reuse terms.
3. Obtain the NEA122 layer payload and data dictionary, including stable station IDs, CRS, active dates and update cadence.
4. Request separate authorised NFA drinking-water compliance aggregates; do not merge potable-network denominators with environmental groundwater stations.
5. Design a privacy-reviewed pilot comparing laboratory results at source and point of use where lawful and feasible.

## შემოწმების სტატუსი

- Source report and public data dictionary reviewed: complete.
- Peer-reviewed method sources checked: complete.
- Independent NOEMA reproduction of the 13% aggregate: pending.
- Georgian sample-level or potable-network validation: blocked by data access.
- Independent water-quality/public-health review: not performed.
- Publication status: draft only.

## ცვლილებების ისტორია

- 2026-11-27: initial source-grounded discovery note; no raw data or personal records added.
