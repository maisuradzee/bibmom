# NOEMA-2026-016 — Georgia drinking-water monitoring frames and public-information gap

- **ID:** NOEMA-2026-016
- **Parent stream:** AquaSignal / NOEMA-2026-006
- **Status:** preliminary
- **Date:** 2026-11-28
- **Scope:** drinking-water sample-frame provenance, public disclosure and operator-facing data quality

## Research question

What do Georgia's official sources establish about planned drinking-water sampling, actual combined food-and-water monitoring results, and public access to geographically useful water-quality information? Which distinctions must AquaSignal preserve before it computes a water-only rate or an early-warning signal?

## Human relevance

The Public Defender's 2025 report describes information-access and monitoring challenges affecting residents, particularly where water services and source types differ. Better structured disclosure could help residents, municipalities and operators understand what was sampled, where, when, against which standard and with what result. This report does not establish that every region lacks monitoring or that a national contamination crisis exists.

## Evidence

### FACT — official NFA 2023 summary

The National Food Agency's 20 February 2024 release reports more than 5,000 samples across **food and drinking water combined**, 624 non-compliances and a rounded 12% violation rate. The exact denominator is not stated in the release, and the scope is mixed. Therefore 12% is **not** a drinking-water-only non-compliance rate and must not be compared directly with water-only secondary-analysis percentages.

### FACT — planned drinking-water sample allocations

The Public Defender's Special Report, pages 33–34, cites the Food Safety State Control Program and an NFA letter (#2024/6048, 4 November 2024). It records planned drinking-water sample counts (including packaged water) of 520 for 2023 and 850 for 2024. These are programme allocations/plans, not evidence that the samples were actually collected, tested or completed.

### FACT — public-information limitation reported by the Public Defender

The report states that the NFA's published monitoring compilation combines multiple food directions and water samples from different source locations (including reservoirs, sources, yard taps and public institutions). Drinking-water information is separated, but the compilation does not readily produce a regional/municipal picture. The Public Defender recommends a consolidated database/platform and communication methods adapted to local contexts, rather than relying only on electronic publication.

The report's fact-finding included visits to 35 villages in 15 municipalities across five regions. This is an oversight/fact-finding exercise, not a representative national water-quality survey.

### FACT — secondary research context

The 2025 JECM article by Bakradze et al. describes a secondary analysis of 2020–2023 drinking-water state-control data and reports that microbiological violations were the main type of non-compliance. The article page identifies the publication date as 1 March 2025. Its PDF tables were not re-extracted in this run, so no exact annual or regional percentage from that paper is newly reproduced here.

### SOURCE-ACCESS LIMIT

The NFA State Control page lists a 2023 monitoring workbook. The linked payload is an XLSX; the current reader rejected the spreadsheet content type. No workbook bytes, row-level contents or SHA-256 were obtained. The official link is an access lead, not an inspected dataset.

## Methodology

1. Reconcile the NFA's official 2023 public release with the Public Defender's official special report and the NFA State Control download index.
2. Separate actual reported combined food/water results from planned drinking-water sample allocations.
3. Record the source's stated scope, period, denominator availability and geography level without deriving missing counts.
4. Cross-check the JECM article's abstract and bibliographic metadata; do not claim a new reproduction of its PDF tables.
5. Add a fail-closed metadata gate that accepts a rate candidate only when the record is an actual drinking-water-only sample result with exact integer numerator/denominator, a sampling frame, indicator/denominator definitions, standard and analytical method.

## Evidence labels and interpretation

- **FACT:** NFA reports 624 non-compliances and 12% across more than 5,000 combined food and drinking-water samples in 2023.
- **FACT:** The Public Defender report records 520 planned drinking-water samples for 2023 and 850 for 2024, including packaged water.
- **FACT:** The Public Defender identifies limitations in regional/municipal interpretability of published monitoring compilations and recommends consolidated disclosure and local communication.
- **REPRODUCED RESULT:** The new synthetic gate tests reject planned allocations, mixed food/water aggregates, boolean counts, missing denominators and missing sampling/standard/method definitions.
- **INFERENCE:** Publicly available summary figures do not currently support a defensible national water-only non-compliance rate. The gap is one of scope and denominator provenance, not proof that the state has no monitoring data.
- **HYPOTHESIS:** A normalized, versioned disclosure layer with explicit water matrix, source type, municipality, planned-versus-actual status, numerator/denominator definitions and publication delay could improve public interpretability and help operators prioritize follow-up.
- **UNTESTED IDEA:** A bilingual municipality-facing water-quality information view with non-technical notices and a source-linked audit trail.

## Innovation: fail-closed monitoring-frame eligibility

`noema_core/monitoring_frames.py` rejects rate calculations when:
- the record is a plan rather than an actual sample result;
- food and drinking-water matrices are combined;
- exact integer numerator/denominator are absent or invalid;
- sampling frame, indicator definition, standard, geography, period or analytical method is missing.

Passing this gate means only that metadata are sufficient to consider a descriptive rate calculation. It is not a potability decision, legal compliance determination, exposure estimate or health-risk assessment.

## Limitations and next steps

- Obtain the official 2023 NFA XLSX and its data dictionary through an authorized route; inspect bytes and calculate SHA-256 before extraction.
- Reconcile planned 520/850 allocations with actual collected, valid, tested and reported drinking-water sample counts.
- Request stable sample/source identifiers, matrix, source type, municipality, collection date, analyte, result, units, LOD/LOQ, method, standard version, numerator/denominator definitions and revision history.
- Keep reservoir, spring, borehole, yard tap, public institution, packaged water, food-contact water, raw groundwater and treated potable network as distinct matrices/scopes.
- Independent public-health, statistical and data-governance review is required before stronger conclusions or publication beyond Preliminary.

No personal records, household locations, private-well coordinates, raw sample rows or restricted payloads are included.
