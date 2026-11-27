# NOEMA-2026-006 — NEA 2025 water-monitoring coverage audit

- **ID:** NOEMA-2026-006
- **Status:** draft / source-grounded aggregate audit
- **Date:** 2026-11-27
- **Source:** National Environmental Agency of Georgia, *2025 annual report*, https://nea.gov.ge/en/Download/File/1444
- **Locator:** Water resources monitoring — groundwater, pp. 10–12; surface waters, p. 13 (page locations from the report contents)

## Research question

What can the publicly accessible NEA 2025 annual report establish about Georgia's groundwater and surface-water monitoring coverage, and which data gaps still prevent AquaSignal from evaluating sample-level water-quality risk?

## Evidence

### FACT — source-reported groundwater activity

The NEA annual report states that 2025 groundwater monitoring covered 124 water points: 74 planned hydrogeological monitoring points and 50 field-instrumental study points. It reports 681 laboratory samples from the 74 planned points, with reported analysis-group counts of 147 chemical, 147 microbiological, 158 heavy-metal, 82 petroleum-product and 147 pesticide samples. These five reported counts sum to 681.

The report separately states that nitrate field-instrumental work collected primary data at 50 points: 19 wells, 30 springs and one household well. It also states that listed physicochemical, major-ion, mineralization, heavy-metal and microbiological parameters were determined at 73 groundwater points.

### FACT — surface-water evidence is separate

The report states that surface-water samples were collected at 238 points and that 2,571 surface-water samples were taken in 2025. This is a separate water matrix and must not be combined with groundwater or potable-network compliance observations.

### REPRODUCED RESULT — arithmetic checks

- 147 + 147 + 158 + 82 + 147 = 681 reported laboratory sample counts.
- 19 + 30 + 1 = 50 nitrate field-study points.

The machine-readable snapshot and tests reproduce these sums from the source-reported aggregates. They do not reproduce any laboratory result or water-quality percentage.

## Interpretation

- **INFERENCE:** The report establishes that NEA performed a substantial, multi-parameter groundwater monitoring programme in 2025 and expanded nitrate-oriented field work. It narrows the earlier discovery gap about whether any recent aggregate monitoring information is publicly available.
- **INFERENCE:** The 73-point parameter-coverage statement and 74-point laboratory-sampling statement are different reported frames until an authorized data dictionary reconciles them.
- **HYPOTHESIS:** An authorized station/sample export with stable identifiers, dates, water matrix, analyte, units, method, LOD/LOQ, lab and QA/QC fields could support a reproducible trend and anomaly-screening pipeline.
- **UNTESTED IDEA:** Combine validated laboratory results with site-approved Water Safety Plan limits and a human-reviewed alert queue; no such thresholds or operational alerts are implemented by this audit.

## Limitations

This annual report does not provide sample-level result values, station/sample IDs, coordinates, sample timestamps, compliance numerator/denominator, the applicable standard/version for each observation, LOD/LOQ, laboratory accreditation scope, QA/QC flags, revision history or data-reuse terms. The 681 counts are not a population denominator, not a non-compliance rate and not proof that water is safe or unsafe.

The 2025 annual report is **not** the separate 2021–2025 groundwater report and nitrate-risk field methodology announced by NEA on 2026-11-26. That announcement links an RAR archive which remains inaccessible to this automated retrieval path; no contents or licence are inferred from the link.

## Next steps

1. Request the authorized station/sample data dictionary and sample-level export, with public/de-identified fields only.
2. Reconcile the 74 laboratory-sampling points, 73 parameter-coverage points and 50 nitrate field-study points.
3. Obtain the NFA drinking-water compliance numerator, denominator, sampling frame, standard/version and supply-type scope separately from NEA environmental-water monitoring.
4. Retrieve the 2021–2025 RAR via an accessible official route and inspect its internal files and reuse terms before extraction.
5. Keep any future alert in shadow mode and require laboratory confirmation and human review before operational action.

No raw sample rows, coordinates, household identities, private-well owner data or health records are included.
