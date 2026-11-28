# NOEMA-2026-009 — AquaSignal: nitrate/nitrite reporting bases and combined-guideline boundary

- **ID:** NOEMA-2026-009
- **Stream ID:** NOEMA-2026-006 (AquaSignal)
- **Record ID:** AQUASIGNAL-GEORGIA-NITRATE-NITRITE-GUIDELINE-CROSSWALK-2026-11-28
- **Status:** preliminary
- **Evidence labels:** FACT / REPRODUCED RESULT (synthetic unit tests only) / INFERENCE / UNTESTED IDEA
- **Date:** 2026-11-28
- **Scope:** WHO drinking-water guidance and Georgia Government Decree №58/2014
- **Structured record:** `data/noema-006/nitrate-nitrite-guideline-crosswalk-2026-11-28.json`

## Research question

How should AquaSignal preserve nitrate and nitrite reporting bases when comparing laboratory results with WHO drinking-water guidance and Georgian Decree №58/2014, and can a combined ratio be calculated without mixing samples, matrices or legal regimes?

## Human benefit and priority

Nitrate/nitrite reporting-basis mistakes can create false reassurance or false alarms. A typed same-sample calculation can prevent a unit mismatch from silently entering a drinking-water screening workflow. No Georgian exposure prevalence or current contamination estimate is available from the sources reviewed.

## Key findings

**FACT — WHO guidance.** The WHO 2026 consolidated fourth edition lists nitrate at 50 mg/L as nitrate ion (NO3-) and nitrite at 3 mg/L as nitrite ion (NO2-). When both occur in drinking-water, the sum of concentration/guideline-value ratios should not exceed 1. The chemical fact sheet is on printed pages 466–472 and states an assessment date of 2016; the 2026 consolidated publication date must not be described as a new nitrate/nitrite reassessment. WHO publishes rounded conversions 0.226 for nitrate ion to nitrate-nitrogen and 0.304 for nitrite ion to nitrite-nitrogen.

**FACT — Georgian drinking-water regulation.** Decree №58/2014, for water within its Article 1 scope, lists nitrate at 50 mg/L as NO3- with a short-term exposure limiting sign and nitrite at 0.2 mg/L as NO2- with a long-term exposure limiting sign. Article 2(21) describes a sum-of-ratios rule for multiple chemicals normalized under the same limiting sign, with radiological components excluded.

**INFERENCE — legal boundary.** Because the table assigns nitrate and nitrite different limiting signs, the text does not support automatically importing the WHO combined nitrate-plus-nitrite ratio as a Georgian legal pass/fail rule. This is a preliminary textual interpretation, not legal advice; independent Georgian legal review is required before any local combined compliance calculation.

**FACT — scope.** Decree №58/2014 has Article 1 scope provisions and exclusions. A result must not be evaluated against the decree without confirming that the specific supply is within scope.

## Primary sources and method

1. World Health Organization, *Guidelines for drinking-water quality: fourth edition incorporating the first, second and third addenda — chemical fact sheets*, 2026-06-17, printed pp. 466–472, PDF pp. 109–114. The nitrate/nitrite assessment date printed in the fact sheet is 2016. [Official WHO PDF](https://cdn.who.int/media/docs/default-source/wash-documents/water-safety-and-quality/dwq-guidelines-4/gdwq_4ed_with_third-addenda_chemical-fact-sheets.pdf?sfvrsn=77d972e1_5).
2. Government of Georgia, Decree №58/2014, 2014-01-15, Article 1(2)–(3), Article 2 Table 4 nitrate/nitrite rows and Article 2(21). [Matsne official text](https://www.matsne.gov.ge/ka/document/view/2196792).

Method: transcribe only the source-published values, units, limiting-sign labels and combined-rule wording; compare WHO guidance with Georgian legal text without assuming the two regimes are interchangeable. No sample-level Georgian data were accessed. No threshold or public alert was changed.

## Reproducible calculation contract

The new helper `noema_core/nitrate_nitrite.py`:

- represents nitrite as Decimal with explicit NO2 or NO2-N basis;
- uses WHO's published rounded 0.304 conversion factor only for basis conversion;
- computes the WHO ratio only when nitrate and nitrite are both on their native ion basis in mg/L;
- requires one pseudonymous sample identifier, one timezone-aware collection timestamp and the exact `drinking_water` matrix;
- refuses raw-groundwater matrices, mismatched analyte matrices, nitrogen-basis inputs to the ratio helper, invalid timestamps, non-finite values, booleans and unsupported units;
- returns the numeric WHO ratio only; it does not produce a Georgian compliance status or declare water safe/unsafe.

The Decimal calculation uses 34 significant digits and ROUND_HALF_EVEN. Conversion factors are rounded source values; preserve original values and bases and do not use converted rounded values alone for near-threshold legal decisions.

## Test results

**REPRODUCED RESULT — synthetic software tests only.** Fourteen focused unit tests and four closed-schema/privacy tests cover conversions, same-sample basis requirements, matrix/time guards, Georgian-vs-WHO threshold separation and absence of private/sample-level data. These are software-contract tests, not water-sample experiments or regulatory validation.

Example synthetic arithmetic: 25 mg/L as NO3- plus 1.5 mg/L as NO2- gives a WHO combined ratio of 25/50 + 1.5/3 = 1.0 for that one synthetic drinking-water sample. This is not a Georgian legal pass/fail result and does not describe a real sample.

## Limitations and competing interpretations

- No paired Georgian nitrate/nitrite sample-level data, laboratory certificates, detection limits, uncertainty budgets or QA/QC records were available.
- No current public sample-level dataset or authorized NEA/NFA data dictionary was verified.
- The WHO factors 0.226 and 0.304 are rounded.
- The Georgian Article 2(21) interpretation requires independent legal review; other amendments, implementing practice or official interpretation may affect application.
- Decree №58/2014 applies only within its Article 1 scope and exclusions.
- The helper does not model analytical uncertainty, censoring below LOD/LOQ, sample preservation, temporal mismatch, treatment-stage differences or laboratory accreditation.
- No clinical risk, potability, public-health exposure or contamination finding is made.

## Innovation and next steps

**Prototype:** a typed, Decimal-based same-sample calculation contract that keeps WHO guidance separate from Georgian legal limits.

Next:
1. Obtain independent Georgian legal review of Article 2(21) and the scope/exclusions in Article 1.
2. Obtain authorized paired nitrate/nitrite laboratory records with sample ID, collection time, matrix, method, LOD/LOQ, uncertainty and QA/QC.
3. Validate unit/basis metadata against the laboratory data dictionary before any shadow-mode calculation.
4. Do not enable an operational alert or legal compliance decision until the sample provenance, applicable legal regime and independent review are confirmed.

## Publication status

Preliminary. No independent legal, analytical-chemistry or laboratory review has been completed. This record is not Published.
