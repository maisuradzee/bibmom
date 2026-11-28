# AquaSignal — NEA 2025 groundwater monitoring coverage audit

**Snapshot date:** 2026-11-28  
**Study:** NOEMA-2026-006  
**Status:** Preliminary / source-reported aggregate audit

## Research question

What can the National Environmental Agency's 2025 annual report establish about groundwater monitoring coverage and nitrate field screening, and which denominators must remain separate until site/sample-level metadata are available?

## Primary source and retrieval

National Environmental Agency of Georgia, *2025 annual report*, section “Water resources monitoring”:
- groundwater monitoring and laboratory-sampling summary: report pp. 10–12;
- nitrate field-instrumental table: report p. 11;
- surface-water monitoring: report p. 13.

Official PDF: https://nea.gov.ge/en/Download/File/1444

The PDF was opened through the public browser reader and the relevant pages were inspected, including the rendered table image. A container-side binary download failed in this run, so the PDF byte-level SHA-256 is **NOT_COMPUTED**. No hash is claimed. This 2025 annual report is distinct from the separate 2021–2025 groundwater RAR and field methodology announced by NEA on 2026-11-26: https://nea.gov.ge/Ge/News/3461. That RAR remains uninspected.

## FACT — source-reported aggregate coverage

The report states:
- **124 combined groundwater monitoring points**, described as 74 routine hydrogeological monitoring points plus 50 field-instrumental study points;
- **two new automatic groundwater stations** were added;
- **74 points** were used for laboratory sampling, with **681 reported laboratory samples/analysis-group counts**:
  - chemical 147;
  - microbiological 147;
  - heavy metals 158;
  - petroleum products 82;
  - pesticides 147;
- a separate statement lists parameter coverage at **73 points**;
- nitrate field-instrumental data were collected at **50 points**:
  - 30 springs;
  - 19 boreholes;
  - 1 **control well**.

The regional nitrate table reports:
| Region | Springs | Boreholes | Control wells | Total |
|---|---:|---:|---:|---:|
| Imereti | 17 | 9 | 1 | 27 |
| Samegrelo-Zemo Svaneti | 0 | 10 | 0 | 10 |
| Samtskhe-Javakheti | 3 | 0 | 0 | 3 |
| Shida Kartli | 7 | 0 | 0 | 7 |
| Mtskheta-Mtianeti | 3 | 0 | 0 | 3 |
| **Total** | **30** | **19** | **1** | **50** |

The source table uses the Georgian term **“საკონტროლო ჭა”**, which means **control well**, not household well. The source-page image was inspected to resolve OCR ambiguity.

The 2025 annual report separately reports surface-water monitoring at **238 points** and **2,571 samples**. These are kept outside the groundwater and drinking-water compliance denominators.

## REPRODUCED_RESULT — deterministic table arithmetic

The public aggregate snapshot and validator reproduce:
- five laboratory analysis-group counts: 147 + 147 + 158 + 82 + 147 = **681**;
- eight regional laboratory rows sum to 681, and each analyte column matches its published aggregate;
- nitrate point types: 30 + 19 + 1 = **50**;
- five regional nitrate rows sum to 50 and match each published point-type total.

Mutation tests change a regional cell while preserving a global column total; the validator rejects the altered row. This reproduces arithmetic from the published table only. It does not reproduce laboratory assays or any water-quality result.

## INFERENCE — what the report does and does not establish

The report establishes that NEA publicly described a 2025 groundwater monitoring programme, laboratory-sampling activity, automatic stations and nitrate-focused field-instrumental work.

It does **not** establish:
- that 124 are 124 unique physical sites;
- whether the 74 laboratory points overlap the 73 parameter-coverage points;
- whether the 50 nitrate field points are identical to all 50 field-instrumental survey points;
- nitrate concentrations, laboratory confirmation, exceedance rates or vulnerable-zone boundaries;
- drinking-water compliance, population exposure or household/private-well safety.

The counts 124, 74, 73, 50, 681, 238 and 2,571 therefore remain separate source-defined reporting frames.

## HYPOTHESIS

If an authorized, privacy-safe export provides stable station/sample IDs, coordinates at an approved precision, collection times, water matrix, analyte, native reporting units, method, LOD/LOQ, laboratory accreditation scope, QA/QC flags and revision history, AquaSignal could support reproducible coverage and trend analysis without conflating environmental groundwater monitoring with potable-network compliance.

## UNTESTED IDEA

AquaSignal could expose a coverage-quality panel showing the distinct 124/74/73/50 reporting frames, missing metadata and data freshness, but it should remain non-alerting until paired laboratory evidence and operator-approved thresholds are available.

## Methodology

1. Re-opened the official NEA 2025 annual-report PDF.
2. Read the text and inspected the rendered page images for the nitrate table and the Georgian control-well term.
3. Transcribed only public regional aggregate counts; no raw sample rows, station IDs, coordinates or owner data were collected.
4. Independently recomputed regional and column totals with a deterministic Python validator.
5. Added closed JSON Schema and mutation tests to detect regional transcription errors that global totals alone would miss.
6. Kept groundwater, surface-water and potable-network compliance evidence separate.

## Limitations and risks

- No sample-level results, station/sample dictionary, exact collection dates, concentrations, units, LOD/LOQ, laboratory accreditation, QA/QC, corrections or reuse licence were available in the annual-report aggregate.
- The report's 74/73/50/124 point frames have no published stable IDs in this snapshot; overlap and unique-site count remain unknown.
- The 681 figure is the report's analysis-group count, not a compliance numerator/denominator or a population estimate.
- The nitrate table is field-instrumental coverage, not a concentration dataset or final vulnerable-zone designation.
- The 2021–2025 RAR announced on 2026-11-26 remains inaccessible to the current binary retrieval route and unhashed.
- No independent hydrogeological, laboratory, statistical or legal review has been obtained.

**Publication decision:** Preliminary only. No independent review has occurred. No Published status or operational safety conclusion is claimed.

**Public-safety boundary:** No exact well coordinates, owner/driller identifiers, private household records, personal data, health records, credentials or restricted source payloads are included.
