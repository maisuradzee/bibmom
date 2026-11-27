# NOEMA-2026-006 — AquaSignal: Georgia monitoring framework and nitrate reporting-basis crosswalk

- **ID:** AQUASIGNAL-GEORGIA-MONITORING-AND-NITRATE-BASIS-2026-11-28
- **სტატუსი:** draft
- **თარიღი:** 2026-11-28
- **Evidence labels:** FACT · REPRODUCED RESULT · INFERENCE · HYPOTHESIS · UNTESTED IDEA
- **Updated:** 2026-11-28
- **Scope:** Georgia environmental water-resource monitoring, historical nitrate indicator metadata and drinking-water control boundaries

## საკვლევი კითხვა

## Research question

How should AquaSignal preserve comparability and provenance when Georgian water-monitoring sources use different nitrate reporting bases, water matrices and monitoring programmes?

## Human benefit and priority

- **Who may benefit:** water-monitoring analysts, laboratories, water-supply operators and public agencies.
- **Potential benefit:** fewer false comparisons caused by mixing nitrate ion (NO3) and nitrate-nitrogen (NO3-N), or environmental-water monitoring with potable-water compliance.
- **Urgency:** high for any future data ingestion because a unit/matrix error can reverse an apparent threshold interpretation.
- **Success measure:** every imported nitrate value retains its original basis, unit, matrix, source, method and sampling frame; any conversion is explicit and reproducible; no legal classification occurs on a converted rounded value alone.

## FACT — Georgia's national water-resource monitoring framework

Government Decree №447 of 15 September 2026 approves the rules for planning and implementing water-resource monitoring and applies from 1 September 2026. The National Environment Agency is the competent authority. It must prepare an annual state water-monitoring plan and submit it for approval by 1 December; monitoring data are to be stored in standardized formats and made accessible subject to environmental-information, data-protection and confidentiality law.

The rule distinguishes observational, operational and investigative monitoring. Operational monitoring is directed at at-risk water bodies and significant pressures and is described as monthly or quarterly. Investigative monitoring is incident/problem-specific. Monitoring points must be representative and selected on a risk basis; the network is periodically reviewed. Until groundwater bodies are defined, the rule applies to hydrogeological units.

The listed Annex 1 and Annex 2 DOCX file was not downloaded or inspected in this run. No annex parameter list, station count or sample frequency is asserted.

## FACT — EEA C11 nitrate units are not uniform across matrices

The ENI SEIS II East / EEA C11 indicator specifies:
- rivers and lakes: nitrate as mg NO3-N/L;
- groundwater: nitrate as mg NO3/L.

The same indicator reports 2016–2017 groundwater data for 34 of 45 listed monitoring sites, sampled twice per year, and describes the result as an aggregate. These are historical environmental-monitoring data, not 2026 measurements or potable-network compliance records.

## FACT — unit conversion reference

WHO's 2022 nitrate/nitrite fact sheet states that 1 mg/L as nitrate ion equals 0.226 mg/L as nitrate-nitrogen. The factor is rounded. AquaSignal's helper uses Decimal arithmetic with this explicit factor and preserves the water-matrix label. It does not apply any threshold, infer potability or combine matrices.

The 2026 WHO Guidelines for Drinking-water Quality (fourth edition incorporating the first, second and third addenda) supersede the earlier edition. The cited 2022 fact sheet is used here only for the stated unit-conversion factor, not as a claim that every 2022 health guideline remains unchanged in 2026.

## FACT — Georgian drinking-water and environmental-water thresholds are distinct

Government Decree №58/2014 lists a nitrate value of 50 mg/L as NO3 and a nitrite value of 0.2 mg/L as NO2 for water within its stated drinking-water scope. EEA C11 separately reports surface-water nitrate maximum permissible concentrations of 45 mg NO3/L (10.2 mg NO3-N/L) for cyprinid waters and 40 mg NO3/L (9.0 mg NO3-N/L) for salmonid waters. These are not interchangeable thresholds.

The 2026 Law №1766 sets 1 September 2027 as the deadline for adoption of a technical regulation on water quality intended for human consumption and other implementing acts. This draft does not infer automatic repeal of Decree №58/2014; current consolidated law and implementing acts require legal review before operational compliance use.

## REPRODUCED RESULT — deterministic unit-conversion tests

Synthetic tests verify:
1. 45 mg/L as NO3 converts to 10.170 mg/L as NO3-N using the cited rounded factor;
2. 10.2 mg/L as NO3-N converts by division by 0.226;
3. matrix labels remain unchanged;
4. Boolean, negative, non-finite, string, unsupported analyte/basis and unsupported units are rejected.

These are unit tests of conversion logic, not new water-sample measurements and not an independent laboratory replication.

## INFERENCE

Because EEA C11 uses different nitrate bases for surface water and groundwater, a data-ingestion pipeline that ignores the basis could create a roughly 4.4-fold scale error. This is a plausible data-quality failure mode, not evidence that any previously published Georgian result was actually misreported.

## HYPOTHESIS

If every observation is stored with explicit water matrix, analyte, reporting basis, unit, sampling point, date, method, LOD/LOQ and source revision, then AquaSignal can compare only valid like-for-like series and flag unit/matrix mismatches before analysis.

## UNTESTED IDEA

Add a source-specific adapter for NEA's 2021–2025 groundwater report after an authorized archive and dictionary are obtained. The adapter should retain raw source values and a separate normalized view, with a provenance link from every transformed value to its source row.

## მეთოდი ან ექსპერიმენტის გეგმა

## Method and limitations

- Reviewed the official Matsne text of Decree №447 and the EEA C11 indicator.
- Reviewed the WHO 2022 nitrate/nitrite conversion statement and the 2026 WHO guideline publication page.
- Reviewed Government Decree №58/2014 and Law №1766 for scope boundaries and transition timing.
- Implemented only a small Decimal-based unit conversion helper with synthetic tests.
- No RAR, NFA XLSX, raw sample file, annex DOCX or restricted dataset was downloaded.
- No current nitrate concentration, contamination prevalence, health exposure or regulatory compliance result is inferred.
- Rounded conversion factor is not suitable as the sole basis for a legal pass/fail decision near a limit.
- Legal status and the future drinking-water regulation require independent Georgian legal review.

## შემოწმების სტატუსი

- Source pages for Decree №447, EEA C11, WHO conversion factor, Decree №58/2014 and Law №1766 were checked on 2026-11-28.
- Decree №447 annex DOCX was listed but not downloaded or inspected.
- The nitrate conversion helper and synthetic tests were added in this branch; GitHub Actions exact-head CI is pending after the draft metadata correction.
- No sample-level data, laboratory results, contamination estimate or compliance decision was generated.

## Innovation

AquaSignal now has a unit-safe nitrate conversion primitive that preserves the original water matrix and refuses unsupported analytes/units. This is a data-quality guard only; it is not a risk score, potability decision or automated public warning.

## წყაროები

1. Government of Georgia, Decree №447, 15 September 2026: https://www.matsne.gov.ge/ka/document/view/7000572
2. ENI SEIS II East / EEA, C11 — Nutrients in freshwater of Georgia: https://eni-seis.eionet.europa.eu/east/indicators/c11-nutrients-in-freshwater-of-georgia
3. WHO, Nitrate and nitrite chemical fact sheet (2022): https://cdn.who.int/media/docs/default-source/wash-documents/water-safety-and-quality/chemical-fact-sheets-2022/nitrate-and-nitrite-fact-sheet-2022.pdf
4. Government of Georgia, Decree №58/2014: https://www.matsne.gov.ge/ka/document/view/2196792
5. Government of Georgia, Law №1766 (24 June 2026): https://manage.matsne.gov.ge/ka/document/view/6904700

## შემდეგი ნაბიჯები

1. Obtain the NEA 2021–2025 archive and official data dictionary through an authorized channel.
2. Inspect Decree №447 Annex 1 and Annex 2 and record only verified parameters/methods.
3. Obtain the NEA 2026 annual monitoring plan after the 1 December submission deadline and compare planned with observed monitoring only when actual collection/result denominators are published.
4. Obtain independent water-chemistry and Georgian legal review before any operational threshold mapping.
