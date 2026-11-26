# NOEMA-2026-006 — Georgia water-data access update

- **Date:** 2026-11-27
- **Status:** discovery / documentary research; no raw monitoring data imported
- **Related work:** [Georgia monitoring-network inventory (2026-11-26)](NOEMA-2026-006-georgia-water-monitoring-inventory-2026-11-26.md)

## Executive finding

The previous inventory's conclusion that no electronic/sample-level material had been identified was too broad. New primary-source review found that Georgia's National Environmental Agency (NEA) has published electronic groundwater monitoring results since 2022, prepares monthly surface-water pollution bulletins, and announced a new 2021–2025 groundwater monitoring report on 2026-11-26. Public historical indicator tables and a water-quality-point map/table entry also exist.

This changes the discovery status from **"public monitoring network descriptions only"** to **"public electronic reports and aggregate tables confirmed; structured sample-level access, schema and reuse terms still unverified."** The new NEA report archive was linked by the Agency, but its RAR contents were not extracted or independently inspected in this run.

## FACT — source-reported evidence

### 1. Groundwater monitoring

The Government of Georgia's 2025 submission to the UNECE/WHO Protocol on Water and Health reports:

- 72 groundwater monitoring points (66 wells and 8 springs);
- 394 laboratory samples collected in 2024, reported as 142 chemical, 137 microbiological, 100 heavy-metal and 15 petroleum-product analyses;
- field studies at 42 points to identify groundwater contaminated with nitrates or at risk of nitrate contamination;
- 12 groundwater information bulletins prepared;
- groundwater monitoring results available electronically since 2022;
- automatic groundwater monitoring-station data collection and control underway.

These are source-reported counts and process descriptions. The report does not itself provide a row-level export, a complete station/analyte data dictionary, or reuse terms in the cited passage.

### 2. New NEA report announced 2026-11-26

NEA announced a 2021–2025 report on fresh groundwater monitoring results and network development, plus a field methodology for identifying nitrate-contaminated or nitrate-risk groundwater. The Agency says the report covers quantitative and qualitative assessment, automatic monitoring systems, processing/digitisation of historical hydrogeological information, and future network development.

The official announcement links a RAR archive:
https://ftp.mepa.gov.ge/Public/NEA/%E1%83%B0%E1%83%98%E1%83%93%E1%83%A0%E1%83%9D%E1%83%92%E1%83%94%E1%83%9D%E1%83%9A%E1%83%9D%E1%83%92%E1%83%98%E1%83%A3%E1%83%A0%E1%83%98%20%E1%83%90%E1%83%9C%E1%83%92%E1%83%90%E1%83%A0%E1%83%98%E1%83%A8%E1%83%98%20-%202026%20-%20%E1%83%94%E1%83%9A-%E1%83%95%E1%83%94%E1%83%A0%E1%83%A1%E1%83%98%E1%83%94%E1%83%91%E1%83%98.rar

The archive is an official lead, not yet an inspected dataset. Its internal files, data granularity, metadata and reuse licence remain unverified.

### 3. Surface-water monitoring

The same UNECE/WHO submission reports sampling at:
- 228 points on 131 water bodies in 2022;
- 243 points on 132 water bodies in 2023;
- 331 points on 137 water bodies in 2024.

It says up to 60 physicochemical parameters and four microbiological indicators are measured, and monthly information bulletins are published. Surface-water observations must remain separate from groundwater and potable-network compliance.

### 4. Drinking-water compliance is a distinct data stream

The UNECE/WHO submission identifies the National Food Safety Agency as the drinking-water quality control body; operating companies conduct internal laboratory control, with independent accredited testing also permitted.

The report records total E. coli non-compliance of 40.3% for 2024, compared with 44.5% for 2023 and 37.0% for 2021–2022. It says the non-compliance was mainly microbiological and that small rural water-supply systems had been included in the laboratory-control programme.

**Interpretation boundary:** the report's table does not provide the denominator or a municipal/system-level breakdown alongside these percentages. 40.3% is a reported sample-compliance statistic, not the percentage of Georgia's population receiving unsafe water, not a current live reading, and not a causal estimate. It is a high-value discovery signal for obtaining the underlying sample counts, locations, dates and corrective-action records from the competent authority.

### 5. Public indicator and map interfaces

- The Water Information System of Georgia publishes C10 (BOD5/ammonium) and C11 (nitrate/phosphate) indicator pages. The displayed annual time series cover 2004–2018; they are historical aggregate indicators, not a current sensor feed.
- Hydromet publishes a page with a "Map of Water Quality Points in Georgia" and an associated table entry. The underlying table's fields, coordinates, export format and freshness were not verified in this run.

## Evidence labels

### FACT
- The 2025 UNECE/WHO report states that groundwater results have been available electronically since 2022 and describes the 2024 monitoring volumes above.
- The same report records 2024 surface-water sampling at 331 points on 137 water bodies and up to 60 physicochemical plus four microbiological indicators.
- The report records E. coli non-compliance of 40.3% in 2024, with small rural systems included in the control programme.
- NEA's 2026-11-26 announcement confirms a 2021–2025 groundwater report and field methodology exist and links an archive.
- WIS C10/C11 expose historical annual aggregates for 2004–2018.

### INFERENCE
- The next AquaSignal bottleneck is no longer simply finding public material. It is extracting and validating the newly identified reports, resolving the correct data owner for each matrix, and obtaining structured sample-level data plus explicit reuse terms.
- The 2024 E. coli statistic justifies prioritising data-access work with the National Food Safety Agency and small-system operators, but it does not by itself identify which municipality, system or population is at risk.

### HYPOTHESIS
If source documents can be transformed into a versioned, provenance-preserving sample catalogue and paired with authorised sensor telemetry, AquaSignal may help operators detect delayed or abnormal results sooner. This remains untested.

### UNTESTED IDEA
A first controlled pilot could compare groundwater nitrate field measurements with laboratory results at a small set of authorised points, while a separate potable-network workstream analyses microbiological compliance and corrective-action latency. These matrices and regulatory owners must never be merged into one score.

## Innovation implications

1. Add source adapters for NEA groundwater bulletins/report archive, NEA surface-water monthly bulletins, and National Food Safety Agency drinking-water compliance records as separate source classes.
2. Use a canonical sample contract with matrix, station/sample ID, coordinates (when authorised), collection and publication timestamps, analyte, value, unit, method, LOD/LOQ, laboratory/accreditation, QA/QC, revision history, applicable standard and source-page provenance.
3. Preserve a distinction between collection time, result-publication time and ingestion time; publication delay is itself an operational metric.
4. Keep the existing rules engine in shadow mode. No national thresholds, public safety status or automated intervention may be inferred from the aggregate report.
5. Before any ingestion, verify archive contents, licensing/reuse terms, data-controller identity, station dictionary and site-specific operational limits.

## Reproducibility and limitations

- No sample-level dataset or RAR archive was downloaded, parsed or hashed in this run.
- No raw personal, operator, laboratory or telemetry data was added to the public repository.
- The UNECE report is a government-submitted summary report, not an independently re-analysed underlying dataset.
- The WIS series are historical and aggregated; they cannot validate current local risk.
- The Hydromet map/table entry is a discovery lead only until its fields and downloadable content are inspected.
- No sensitivity, specificity, positive predictive value, false-alert rate or detection delay was calculated.

## Sources

1. **National Environmental Agency of Georgia**, 2026-11-26, *2021–2025 groundwater monitoring results and field methodology announcement*: https://nea.gov.ge/ajs/News/3461
2. **Government of Georgia**, 2025-04-01 submission, *Summary report under the Protocol on Water and Health*, especially pp. 26, 42, 51 and 56: https://unece.org/sites/default/files/2025-10/Georgia_summary_report_6th_cycle_1Apr25_ENG.pdf
3. **Water Information System of Georgia**, C10 BOD5/ammonium indicator: https://wis.mepa.gov.ge/Wis/C10?Id=2121
4. **Water Information System of Georgia**, C11 nutrients indicator: https://wis.mepa.gov.ge/Wis/C11?Id=2122
5. **Hydromet Georgia**, maps and water-quality-points table entry: https://www.hydromet.ge/maps/
6. **National Environmental Agency of Georgia**, water-monitoring network announcement, 2025-09-18: https://nea.gov.ge/En/News/2335

## Next steps

1. Obtain and inspect the official 2021–2025 RAR archive; record archive hash, internal filenames, page/table references and whether any structured data are included.
2. Retrieve the 2022–2025 groundwater bulletins and monthly surface-water bulletins; determine whether their tables are machine-readable and revision-stable.
3. Inspect the Hydromet water-quality-points table and WIS C10/C11 table exports; document fields, units, period, station coverage and source lineage.
4. Request the denominator and geographic/system disaggregation behind the 2024 E. coli 40.3% figure from the National Food Safety Agency; seek written data access/reuse terms.
5. Only after approval, select one matrix and one pilot operator for a preregistered retrospective/shadow-mode validation.

- **Status:** draft; no promotion to preliminary or published.
