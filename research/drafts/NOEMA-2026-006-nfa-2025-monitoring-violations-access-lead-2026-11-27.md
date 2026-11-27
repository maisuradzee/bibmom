# NOEMA-2026-006 — NFA 2025 drinking-water monitoring-violations access lead

- **ID:** NOEMA-2026-006
- **Status:** draft
- **Date:** 2026-11-27
- **Pillars:** DISCOVERY · RESEARCH · INNOVATION
- **Evidence class:** primary-source discovery; payload not retrieved
- **Related work:** [Georgia water-data access update](NOEMA-2026-006-georgia-water-data-access-update-2026-11-27.md)

## Research question

Does the National Food Agency's published 2025 monitoring-violations file provide a lawful, machine-readable route to water-specific sample evidence, and what is still required before it can support an interpretable drinking-water compliance measure?

## FACT — official page and published context

The National Food Agency page **“2025 წელს გამოვლენილი დარღვევები”**, dated 2026-01-08, states that the Food Department carried out 21,874 inspections in 2025, including 9,241 planned, 1,833 unplanned and 279 recognition-related inspections; it says 10,521 business operators were rechecked and critical non-compliance was identified at 554 operators.

The same page links a downloadable file described as violations found in food and drinking-water monitoring samples:

- Landing page: https://nfa.gov.ge/Ge/IdentifiedViolations/1713
- File endpoint: https://nfa.gov.ge/Ge/Files/Download/8918

The available web retrieval path identified the response as an XLSX (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet) but could not return the binary payload. A direct container download attempt also failed. No file bytes, worksheet names, row count, columns, digest or data dictionary were obtained.

## Why this is useful — and what it does not prove

This is a new official access lead for NFA monitoring-violation records. It is distinct from NEA groundwater and surface-water monitoring, and distinct from the WRP self-reported global drinking-water harm indicator.

The linked file is described as covering **food and drinking-water sample violations together**. The landing page does not disclose a water-only sample denominator or the complete universe of samples tested. A violations-only extract is not a prevalence denominator. Therefore this lead does not resolve the missing denominator for the separate 2024 E. coli non-compliance figure in the Georgia Protocol on Water and Health report.

## Evidence classification

### FACT
- The official page date and administrative totals above are source-reported.
- The page links file endpoint /Ge/Files/Download/8918 for violations identified in food/drinking-water monitoring samples.
- The retrieval response was identified as XLSX, but the payload was not retrieved.

### INFERENCE
- The NFA file may help identify the structure of publicly disclosed enforcement evidence and guide a formal request for water-specific sample counts.
- If the file contains only non-compliant samples, it cannot estimate the non-compliance rate without the full tested-sample denominator and sampling frame.

### HYPOTHESIS
If NFA can provide a de-identified, authorized export with water-matrix labels, collection period, analyte, result, unit, method, denominator and geographic/system grouping, AquaSignal could build a provenance-preserving monitoring summary without exposing operator or personal details.

### UNTESTED IDEA
A future source adapter could ingest an authority-approved aggregate export into a private staging environment, validate its schema and provenance, and publish only disclosure-reviewed aggregates. It must not merge potable-water compliance records with NEA environmental groundwater or surface-water observations.

## Method

1. Opened the official NFA page and recorded only its public administrative summary and file link.
2. Followed the file link; the browser retrieval layer rejected the XLSX response as an unsupported binary content type.
3. Attempted a direct download from the same official URL; the runtime download failed.
4. Recorded the access lead as metadata only. No workbook parsing, checksum, row-level analysis or reuse decision was performed.

## Data and privacy requirements before ingestion

- Obtain the exact file bytes through an authorized channel and calculate SHA-256 locally.
- Inspect the workbook in a controlled/private workspace before any publication decision.
- Identify whether it contains personal data, business-operator identifiers, addresses, exact sampling locations or other restricted fields; do not commit the raw workbook.
- Obtain the worksheet/column dictionary, water-matrix definitions, period, sampling frame, tested-sample denominator, laboratory methods, units, QA/QC and revision history.
- Confirm explicit reuse and redistribution terms with the data controller.
- Keep food, potable drinking water, groundwater, surface water and marine water as separate matrices and source classes.

## Limitations

- The XLSX payload was not retrieved, hashed or inspected.
- No claim is made about workbook row count, columns, sample counts, non-compliance counts, geography or data granularity.
- The published inspection totals are not drinking-water sample totals.
- The file endpoint is described as combined food/drinking-water violations; no water-only denominator is published on the landing page.
- This 2025 lead cannot repair the missing denominator in the distinct 2024 E. coli statistic.
- No local prevalence, current contamination status, public-health outcome or causal claim is made.
- Reuse terms and public redistribution rights remain unverified.

## Sources

1. **National Food Agency of Georgia**, 2026-01-08, *2025 წელს გამოვლენილი დარღვევები*: https://nfa.gov.ge/Ge/IdentifiedViolations/1713
2. **National Food Agency of Georgia**, official linked XLSX endpoint: https://nfa.gov.ge/Ge/Files/Download/8918

## Next steps

1. Request the NFA's water-specific sample denominator and an authorized data dictionary/export.
2. Inspect the workbook privately only after the data controller's access and reuse conditions are clear.
3. If a complete sampling frame is unavailable, retain the file as enforcement discovery evidence only and do not calculate a rate.
4. Independently review the data-protection and public-disclosure plan before any aggregate is added to the public catalogue.
