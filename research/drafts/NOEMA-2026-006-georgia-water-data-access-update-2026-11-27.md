# NOEMA-2026-006 — Georgia water-data access update

- **ID:** NOEMA-2026-006
- **სტატუსი:** draft
- **თარიღი:** 2026-11-27
- **სფერო:** საზოგადოებრივი ჯანმრთელობა · წყლის მონიტორინგი · მონაცემთა წვდომა
- **ავტორი/მომზადების სისტემა:** NOEMA research workflow
- **Related work:** [Georgia monitoring-network inventory (2026-11-26)](NOEMA-2026-006-georgia-water-monitoring-inventory-2026-11-26.md)

## საკვლევი კითხვა

რომელი ახალი ოფიციალური წყაროები და ელექტრონული ანგარიშები იძლევა AquaSignal-ისთვის ნებადართული, provenance-იანი წყლის ხარისხის მონაცემების მიღების რეალურ შესაძლებლობას და რა მონაცემთა/უფლებების ბარიერები რჩება?

## Executive finding

The previous inventory's conclusion that no electronic/sample-level material had been identified was too broad. New primary-source review found that Georgia's National Environmental Agency (NEA) has published electronic groundwater monitoring results since 2022, prepares monthly surface-water pollution bulletins, and announced a new 2021–2025 groundwater monitoring report on 2026-11-26. Public historical indicator tables and a water-quality-point map/table entry also exist.

This changes the discovery status from **"public monitoring network descriptions only"** to **"public electronic reports and aggregate tables confirmed; structured sample-level access, schema and reuse terms still unverified."** The new NEA report archive was linked by the Agency, but its RAR contents were not extracted or independently inspected in this run.

## FACT — source-reported evidence

### 1. Groundwater monitoring

The Government of Georgia's 2025 submission to the UNECE/WHO Protocol on Water and Health reports:

- 72 groundwater monitoring points (66 wells and 8 springs);
- 394 laboratory samples collected in 2024 from the 72 network points, reported as 142 chemical, 137 microbiological, 100 heavy-metal and 15 petroleum-product samples;
- automatic stations installed on wells and springs in 11 district units across 8 regional administrations during 2022–2024;
- field studies at 42 points to identify groundwater contaminated with nitrates or at risk of nitrate contamination;
- 12 groundwater information bulletins prepared and published;
- groundwater monitoring results available electronically since 2022;
- automatic groundwater monitoring-station data collection and control underway.

The government-submitted report also characterises groundwater used as a drinking-water source as generally good quality, while noting isolated microbiological exceedances and average values within limits. This is the report's own summary, not an independent re-analysis. The report does not itself provide a row-level export, a complete station/analyte data dictionary, or reuse terms in the cited passage.

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

The report narrative records total E. coli non-compliance of 37.0% for 2021–2022, 44.5% for 2023 and 40.3% for 2024. A separate table on page 56 labels its columns as baseline 2005 (25.0%), previous reporting cycle 2019 (34.0%) and current 2024 (40.3%). These are different reference-year frames in the same submission and must not be joined into one continuous trend without the underlying definitions and denominators. The report says non-compliance was mainly microbiological and that small rural water-supply systems had been included in the laboratory-control programme.

**Interpretation boundary:** the report's E. coli table does not provide the sample denominator or an urban/rural or municipal/system-level breakdown. Its context section separately reports that up to 70% of the population is connected to centralised supply (95% urban and 35% rural) and 31% uses other local supply systems, but it does not explicitly tie those coverage figures to the 40.3% sample frame. The 40.3% is a reported sample-compliance statistic, not the percentage of Georgia's population receiving unsafe water, not a current live reading, and not a causal estimate. The differing narrative/table reference years and absent denominators make trend reconstruction unsafe without the underlying methodology and counts. It is a high-value discovery signal for obtaining the underlying sample counts, locations, dates and corrective-action records from the competent authority.

### 5. Public indicator and map interfaces

- The Water Information System of Georgia publishes C10 (BOD5/ammonium) and C11 (nitrate/phosphate) indicator pages. The displayed annual time series cover 2004–2018; they are historical aggregate indicators, not a current sensor feed.
- Hydromet publishes a page with a "Map of Water Quality Points in Georgia" and an associated table entry. The underlying table's fields, coordinates, export format and freshness were not verified in this run.

## Evidence labels

### FACT
- The 2025 UNECE/WHO report states that groundwater results have been available electronically since 2022 and describes the 2024 monitoring volumes above.
- The same report records 2024 surface-water sampling at 331 points on 137 water bodies and up to 60 physicochemical plus four microbiological indicators.
- The report narrative records E. coli non-compliance of 37.0% (2021–2022), 44.5% (2023) and 40.3% (2024); its separate table labels 25.0% (2005), 34.0% (2019) and 40.3% (2024). The table leaves sample denominator and urban/rural disaggregation blank, so these reference frames are not merged into one trend.
- The same government submission describes groundwater used as a drinking-water source as generally good quality, with isolated microbiological exceedances and averages within norms; this remains source-reported evidence.
- NEA's 2026-11-26 announcement confirms a 2021–2025 groundwater report and field methodology exist and links an archive.
- WIS C10/C11 expose historical annual aggregates for 2004–2018.

### INFERENCE
- The next AquaSignal bottleneck is no longer simply finding public material. It is extracting and validating the newly identified reports, resolving the correct data owner for each matrix, and obtaining structured sample-level data plus explicit reuse terms.
- The 2024 E. coli statistic justifies prioritising data-access work with the National Food Safety Agency and small-system operators, but it does not by itself identify which municipality, system or population is at risk.

### HYPOTHESIS
If source documents can be transformed into a versioned, provenance-preserving sample catalogue and paired with authorised sensor telemetry, AquaSignal may help operators detect delayed or abnormal results sooner. This remains untested.

### UNTESTED IDEA
A first controlled pilot could compare groundwater nitrate field measurements with laboratory results at a small set of authorised points, while a separate potable-network workstream analyses microbiological compliance and corrective-action latency. These matrices and regulatory owners must never be merged into one score.

## შემოწმების მეთოდი


1. Add source adapters for NEA groundwater bulletins/report archive, NEA surface-water monthly bulletins, and National Food Safety Agency drinking-water compliance records as separate source classes.
2. Use a canonical sample contract with matrix, station/sample ID, coordinates (when authorised), collection and publication timestamps, analyte, value, unit, method, LOD/LOQ, laboratory/accreditation, QA/QC, revision history, applicable standard and source-page provenance.
3. Preserve a distinction between collection time, result-publication time and ingestion time; publication delay is itself an operational metric.
4. Keep the existing rules engine in shadow mode. No national thresholds, public safety status or automated intervention may be inferred from the aggregate report.
5. Before any ingestion, verify archive contents, licensing/reuse terms, data-controller identity, station dictionary and site-specific operational limits.

## შემოწმების სტატუსი


- No sample-level dataset or RAR archive was downloaded, parsed or hashed in this run.
- No raw personal, operator, laboratory or telemetry data was added to the public repository.
- The UNECE report is a government-submitted summary report, not an independently re-analysed underlying dataset.
- The WIS series are historical and aggregated; they cannot validate current local risk.
- The Hydromet map/table entry is a discovery lead only until its fields and downloadable content are inspected.
- No sensitivity, specificity, positive predictive value, false-alert rate or detection delay was calculated.

## წყაროები

1. **National Environmental Agency of Georgia**, 2026-11-26, *2021–2025 groundwater monitoring results and field methodology announcement*: https://nea.gov.ge/ajs/News/3461
2. **Government of Georgia**, 2025-04-01 submission, *Summary report under the Protocol on Water and Health*, especially pp. 26, 42, 51 and 56: https://unece.org/sites/default/files/2025-10/Georgia_summary_report_6th_cycle_1Apr25_ENG.pdf
3. **Water Information System of Georgia**, C10 BOD5/ammonium indicator: https://wis.mepa.gov.ge/Wis/C10?Id=2121
4. **Water Information System of Georgia**, C11 nutrients indicator: https://wis.mepa.gov.ge/Wis/C11?Id=2122
5. **Hydromet Georgia**, maps and water-quality-points table entry: https://www.hydromet.ge/maps/
6. **National Environmental Agency of Georgia**, water-monitoring network announcement, 2025-09-18: https://nea.gov.ge/En/News/2335

## შემდეგი ნაბიჯები

1. Obtain and inspect the official 2021–2025 RAR archive; record archive hash, internal filenames, page/table references and whether any structured data are included.
2. Retrieve the 2022–2025 groundwater bulletins and monthly surface-water bulletins; determine whether their tables are machine-readable and revision-stable.
3. Inspect the Hydromet water-quality-points table and WIS C10/C11 table exports; document fields, units, period, station coverage and source lineage.
4. Request the denominator and geographic/system disaggregation behind the 2024 E. coli 40.3% figure from the National Food Safety Agency; seek written data access/reuse terms.
5. Only after approval, select one matrix and one pilot operator for a preregistered retrospective/shadow-mode validation.

- **Status:** draft; no promotion to preliminary or published.

## ცვლილებების ისტორია

- 2026-11-27: დაემატა UNECE/WHO-ის 2025 ანგარიშისა და NEA-ის 2026-11-26 განცხადების საფუძველზე მონაცემთა წვდომის განახლება; არქივის შიგთავსი ჯერ არ შემოწმებულა.


## 6. New well-registration system — Government Resolution No. 424

### FACT — legal scope and required data

Government of Georgia Resolution No. 424 was adopted on 31 August 2026 and took effect on 1 September 2026. It establishes a state accounting procedure for wells drilled to extract fresh drinking water where the well depth exceeds 20 metres. The legal text excludes mineral, thermal and medicinal/balneological groundwater and wells drilled before the regulation took effect. NEA's public notice additionally states that household wells on citizens' household plots are excluded, whether built before or after 1 September 2026.

The regulation requires NEA to create and periodically update a hydrogeological database from submitted well passports. The driller must submit the passport within 15 working days after drilling is completed; NEA must notify the driller about inclusion in the database within 10 working days after receiving the data. NEA may also conduct field monitoring and laboratory sampling where location and hydrogeological conditions warrant it.

The passport fields include coarse and precise location data (including UTM coordinates and, where available, cadastral code), owner identity and contact details, drilling date, well construction, geology/hydrogeology, static/dynamic water levels and yield. Field-test and laboratory-analysis results are attached **if sampling/analysis was performed**; the regulation does not establish that every registered well necessarily has a laboratory result.

### INFERENCE — what this changes for AquaSignal

This is a new prospective administrative data source, not evidence of a complete national well inventory or a public water-quality time series. It does not cover pre-existing wells under the legal text, and NEA says household wells are outside the rule. A registration passport can contain useful hydrogeological metadata, but its existence alone does not imply repeated sampling, public access, a live API, or permission for secondary use.

AquaSignal must therefore maintain separate source classes:
1. NEA groundwater monitoring stations and sample results;
2. the new post-1 September 2026 well-registration database;
3. household and pre-existing wells outside the stated registration scope;
4. potable-network compliance sampling owned by the competent drinking-water control authorities.

These classes must not be merged into one coverage denominator or one water-safety score.

### PRIVACY AND PUBLICATION BOUNDARY

The legal annex explicitly requests personal identity and contact information for well owners and drillers, alongside well coordinates. No such records, identifiers, coordinates or owner details were accessed or copied. The public repository contains only the legal source URL, scope metadata and a description of the data categories.

Any future access must use a written authorization and a privacy-reviewed, purpose-limited export. Prefer aggregated or de-identified records; do not mirror the administrative register into the public repository. The legal text and NEA announcement do not establish that the database or its records are publicly downloadable.

### HYPOTHESIS

If NEA can provide an authorized, de-identified well-register extract with stable well IDs, hydrogeological attributes and optional laboratory-result provenance, it may help prioritise monitoring gaps and nitrate-risk field follow-up. It cannot replace routine sampling or establish potable safety without representative laboratory evidence.

### UNTESTED IDEA

A registry-to-monitoring crosswalk could identify which newly registered wells have no recent field or laboratory sample and support a transparent, operator-approved sampling-priority list. This requires a lawful registry export, a data dictionary, sampling history, and an agreed definition of a monitoring gap.

### New source

- Government of Georgia, Resolution No. 424, 31 August 2026, *Technical Regulation — Rules for Accounting Wells for the Extraction of Fresh Drinking Groundwater*, effective 1 September 2026: https://matsne.gov.ge/ka/document/view/6991245
- National Environmental Agency, *New state accounting regulation for fresh drinking-water wells entered into force on 1 September*, 1 September 2026: https://nea.gov.ge/En/News/2430

### Verification status

The legal text and NEA notice were inspected. The registry itself, its operational database, data dictionary, API, public access policy, historical coverage and sample-level records were not inspected. The 2021–2025 NEA RAR archive announced on 26 November also remains unextracted. No field validation or water-quality model result is claimed.
