# AquaSignal — public information and accessibility gap in drinking-water quality

- **ID:** NOEMA-2026-006 (AquaSignal addendum)
- **Status:** draft
- **Date:** 2026-11-27
- **Scope:** Georgia; public drinking-water information, source provenance and access
- **Author/preparation system:** NOEMA documentary research and engineering synthesis

## Research question

Can an authority-owned, provenance-aware public-information layer make approved drinking-water monitoring results easier to find and understand, while preserving sample context, uncertainty, privacy and the legal authority of the responsible agencies?

## Short summary

The strongest new AquaSignal finding is not proof that drinking water is nationally unsafe. It is a documented public-information and accountability problem: the Public Defender of Georgia's 2025 special report says that residents' lack of information about water quality was one of the main challenges observed during monitoring visits, and recommends a unified public-information platform/database together with supplementary dissemination channels.

The report describes visits to five regions, 35 villages and 15 municipalities. It records incomplete or contradictory municipal responses in some cases. These observations are important, but they are not a probability sample of all Georgian settlements and cannot be converted into a national prevalence rate.

The public monitoring figures also need careful treatment. A 2025 JECM article describes a secondary analysis of National Food Agency monitoring data and reports 49.5% broad technical-regulation non-compliance among samples in 2023. The Government of Georgia's report submitted through the UNECE/WHO reporting system reports 44.5% broad non-compliance for 2023. The five-percentage-point difference remains unreconciled. The Government submission is not an independent UNECE/WHO survey, and its E. coli table is a separate indicator context.

The practical opportunity is therefore an **authority-owned disclosure and accessibility layer**, not a new independent water-safety score or alert authority.

## Why this question matters

People cannot make informed decisions or challenge service failures if official monitoring information is difficult to locate, poorly explained, stale or only communicated verbally. This affects transparency and accountability even where laboratory monitoring exists.

AquaSignal already distinguishes environmental-water monitoring from potable-network compliance and treats sensor/laboratory signals as operator decision support. This addendum extends the human-benefit pathway: a result is useful only if its source, sample context, interpretation authority and publication status are understandable to the people who need it.

## Existing knowledge and sources

1. **Public Defender (Ombudsman) of Georgia, _Realisation of the Right to Water in Georgia_, 2025.** The report was prepared by the Office of the Public Defender with assistance from UN/UNDP and other partners; it states that its contents are the author's responsibility. Relevant locators: PDF p.34 (information gap), p.37 (five regions, 35 villages, 15 municipalities and municipal information inconsistencies), pp.49-51 (examples of information access), p.54 (recommendations for a unified platform and supplementary channels).  
   URL: https://www.undp.org/sites/g/files/zskgke326/files/2025-06/undp-georgia-pdo-report-right-to-water-eng.pdf

2. **Bakradze, L. et al., _State control and monitoring trends of drinking water quality in Georgia_, Experimental and Clinical Medicine Georgia, 2025/1, DOI 10.52340/jecm.2025.01.25.** The article describes a secondary hygienic analysis of NFA monitoring data for 2020-2023. Relevant locators: PDF pp.1-3, especially the Methods and 2023 rate. The journal's formal peer-review procedure was not independently verified from accessible policy pages.  
   URL: https://journals.4science.ge/index.php/jecm/article/download/3442/3462

3. **Government of Georgia, _Summary reports in accordance with Article 7 of the Protocol on Water and Health — Georgia_, submitted 2025-04-01 through the UNECE/WHO reporting system.** This is a government submission, not an independent UNECE/WHO survey. Relevant locators: PDF p.1 (submission status), p.16 (broad non-compliance narrative), pp.54-56 (sample-source response and E. coli table).  
   URL: https://unece.org/sites/default/files/2025-10/Georgia_summary_report_6th_cycle_1Apr25_ENG.pdf

## Evidence classification

### FACT

- The Public Defender's report says that lack of information about drinking-water quality among residents was one of the main challenges identified during monitoring visits (p.34).
- The Public Defender reports visits to five regions, 35 villages and 15 municipalities, resident interviews and written information requests to municipalities; some responses were missing, incomplete or differed from residents' accounts (p.37).
- The report recommends a unified platform/database for simple, understandable public information on drinking-water quality-control results and supplementary mechanisms beyond the online platform (p.54).
- The JECM article states that it is a secondary analysis of NFA monitoring data for 2020-2023 and reports 49.5% broad non-compliance among 2023 monitoring samples.
- The Government of Georgia's submitted report states 44.5% broad non-compliance in 2023 and 40.3% in 2024; its Table 4.i is specifically about E. coli and must not be conflated with the broad all-standard narrative.

### REPRODUCED RESULT

No new numerical result is claimed in this addendum. The five-percentage-point difference (49.5% versus 44.5%) is arithmetic on the two published figures, not a reproduction from raw samples.

### INFERENCE

A high-value AquaSignal opportunity is to improve the provenance, comprehensibility and accessibility of authorized public monitoring information. The documentary evidence does not show that monitoring is absent; it shows that the public-information pathway can fail even when control and testing activities exist.

### HYPOTHESIS

If authorized results are published with clear sample context, indicator definitions, freshness, correction history and non-digital access routes, residents and local service partners may understand official water-quality information more reliably.

### UNTESTED IDEA

A bilingual, low-bandwidth result page with printable municipal notices, authority-approved phone/community channels and a correction-request path may be a practical interface for an authority-owned disclosure service.

## Competing explanations

- The report's municipal observations may reflect particular settlements and visit selection rather than a nationwide pattern.
- Information may be available through channels not captured in the report or may have improved after 2025.
- The difference between the JECM and Government-submitted 2023 percentages may arise from different sample frames, definitions, reporting periods or aggregation rules; the available public documents do not resolve which explanation applies.
- More visible information does not necessarily improve comprehension or protective behaviour without accessible language, trusted channels and a response mechanism.

## Hypothesis and proposed architecture

The responsible public authority should own the data, interpretation, correction and any safety notice. NOEMA's role would be limited to validating provenance/completeness and rendering approved information.

Required components:

1. **Source registry:** responsible authority, legal basis, official URL, licence/reuse terms, data owner and revision policy.
2. **Result record:** water matrix (potable network, groundwater source, surface water or bottled water), sample frame, point type, sampling date, analyte, result, unit, method, laboratory/accreditation status, QA flags, applicable standard/version, denominator where relevant, publication date and correction history.
3. **Publication state:** explicitly distinguish current, delayed, withdrawn, corrected, not yet published and unavailable. Missing data must remain unknown, never “safe”.
4. **Accessible dissemination:** authority-approved web, printable, phone and community channels; an online-only interface is insufficient.
5. **Correction and provenance:** retain source references and version events so a corrected result does not silently overwrite the earlier public record.

### Privacy and authority boundaries

- Do not ingest personal names, contact details, household records, exact private-well coordinates or individual health data.
- Use only authority-approved spatial precision and suppress small cells where re-identification is possible.
- Do not combine groundwater, surface-water and potable-network indicators into a single score.
- Do not issue an independent “safe/unsafe” label, medical advice or official warning.
- Do not infer safety from missing, stale or non-published results.

## Method

This addendum is a documentary synthesis of the three cited public documents, with page-level claim locators and explicit source-role classification. It does not reproduce raw NFA samples, inspect a private or sample-level database, survey residents, audit a current municipal portal or test an operational interface.

## Results and interpretation

The evidence supports a concrete research and product requirement: public monitoring information should be source-linked, contextualized and accessible through more than one channel. It does **not** support a current national water-risk score, municipal ranking, causal health claim or operational alert.

The 2023 49.5% and 44.5% figures remain unresolved. Neither should be selected as the “correct” value or averaged. The 2024 E. coli-specific 40.3% table entry must remain distinct from the broad all-standard narrative, even though the same numeric value appears.

## Success measures for a future authorized pilot

- Share of published records with complete source, sample-frame, date, method, unit, standard and denominator metadata.
- Time from official result release to accessible public availability.
- Correction/withdrawal latency and proportion of corrected records with preserved revision history.
- Channel availability and delivery counts reported separately by channel; endpoint receipts must not be labelled as unique people reached.
- Comprehension and usability measured through an approved, voluntary and appropriately sampled evaluation.
- Zero unauthorized personal/private-well fields and zero NOEMA-generated safety classifications.

## Limitations and uncertainty

- Documentary synthesis only; NOEMA conducted no field visits, interviews or municipal verification.
- The Public Defender's visits are not a nationally representative probability sample.
- JECM's 49.5% and the Government submission's 44.5% broad 2023 indicators remain unreconciled.
- The published aggregates do not supply raw sample-level data or enough sample-frame detail for operational local signals.
- No current public-information platform inventory, accessibility audit or user-comprehension baseline has been completed.
- No authority approval, data-sharing agreement, API integration or operational prototype exists.

## Conclusion

AquaSignal should investigate public information access alongside monitoring-data quality. The next defensible step is to obtain an authority-approved data dictionary, denominator/sample-frame definitions, publication/correction rules and a map of existing citizen-information channels. Only then should an interface prototype be evaluated. This addendum remains **Draft** and is not a water-safety assessment.

## Change history

- 2026-11-27: Added a Public Defender evidence-led public-information/accessibility research question, preserved the JECM/Government-submission discrepancy, and specified an authority-owned, privacy-preserving disclosure architecture.
