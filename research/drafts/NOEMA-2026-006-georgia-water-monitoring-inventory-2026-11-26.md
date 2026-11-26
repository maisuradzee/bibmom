# NOEMA-2026-006 — Georgia water-monitoring network inventory

- **Date:** 2026-11-26
- **Status:** draft / public-source inventory only; no sample-level laboratory data was obtained or imported
- **Research stream:** AquaSignal

## Research question

Which existing Georgian water-monitoring networks and official data sources could support AquaSignal's early-signal layer without duplicating or replacing the responsibilities of the National Environmental Agency, the water utility or accredited laboratories?

## FACT — official source disclosures

1. **NEA surface and groundwater network (18 September 2025).** The National Environmental Agency reports surface-water monitoring at 238 locations throughout the year and groundwater monitoring at 72 water points. The same notice describes a separate Black Sea monitoring network of 12 locations and states that the agency's air, water and soil laboratory is ISO/IEC 17025 accredited. These are source-published network counts, not a downloadable sample dataset.
2. **NEA Black Sea update (13 July 2026).** The agency reports monthly Black Sea monitoring at 14 points and lists hydrobiological and chemical parameters, including 13 heavy metals, total petroleum hydrocarbons, 16 polyaromatic hydrocarbons and other physicochemical parameters. Its statement that sampled coastal water was within norms is limited to that marine monitoring context and the samples considered in the notice; it is not a drinking-water or nationwide freshwater assessment.
3. **United Water Supply Company laboratory network (undated public information page, accessed 26 November 2026).** The company describes 8 regional laboratories and 35 service-centre laboratories. It names regional locations in Bolnisi, Gori, Tskaltubo, Kutaisi, Ozurgeti, Poti, Akhaltsikhe and Telavi. The page says raw-source and treated-network water are monitored under technical regulations and an approved schedule, with organoleptic, chemical and microbiological analyses performed daily. The page does not expose a station-by-station sampling calendar or sample-level results.
4. **NEA water-resources page (undated, accessed 26 November 2026).** It describes monitoring responsibilities across the agency's environmental-pollution, hydrometeorology and geology departments and distinguishes groundwater, surface and coastal waters.

The counts above describe different networks and dates. They must not be added into a single national station total or interpreted as equivalent coverage.

## INFERENCE — opportunity and gap

Georgia already has institutional monitoring infrastructure and accredited laboratory capacity. AquaSignal's potential role is therefore an evidence-linked early-signal and workflow layer that helps authorized operators notice anomalies and route them for confirmation; it must not duplicate regulatory testing or issue an independent declaration that water is safe.

The public pages inspected disclose network capacity, broad parameter classes and laboratory processes, but not a machine-readable sample-level time series, complete station registry, full data dictionary, API contract or explicit reuse terms. This is a source-access gap, not proof that no such data exists internally or elsewhere.

## HYPOTHESIS

If authorized sensor telemetry can be linked to timely, traceable laboratory samples and site-specific Water Safety Plan limits, AquaSignal may help reduce the time between an abnormal signal and a verified operator response. This has not been tested with Georgian operational data.

## UNTESTED IDEA — data contract and pilot sequence

Before building an ingestion adapter, obtain a documented data contract containing:

- station ID, coordinates, sample ID and sample timestamp;
- water matrix: raw source, treated network, surface water, groundwater or marine water;
- analyte, result, unit, analytical method, LOD/LOQ and uncertainty where available;
- laboratory identity, accreditation scope, QA/QC flags and sample custody;
- applicable legal standard and the separately approved site Water Safety Plan limit;
- publication/receipt timestamp, revision and correction history;
- data ownership, access control, retention and written reuse permission.

A future pilot should remain in **shadow mode** until the data controller and site operator approve it. Pre-register detection delay, sensitivity, positive predictive value, false alerts per station-month, data completeness and sensor-calibration drift. Every alert must show source, sample age, parameter, unit, threshold provenance and uncertainty, and require laboratory/operator confirmation before action.

## Safety and evidence limits

- Surface-water, groundwater, marine-water and potable-network observations are different matrices and must never share thresholds without an approved technical basis.
- The 2026 NEA Black Sea statement cannot be used to infer drinking-water safety or freshwater conditions.
- A network count does not establish sampling frequency at each site, public data availability, representativeness or current compliance.
- No thresholds, WHO guideline values or legal limits are copied into the prototype from these news summaries.
- No sensor readings, laboratory results, personal data, operator telemetry, credentials or private documents were used.

## Next steps

1. Search the agency's public water-resource reports and result publications for machine-readable sample records and their metadata.
2. Obtain the official station registry, sampling schedule, analyte dictionary, analytical methods, QA/QC and reuse terms through an authorized public-information channel.
3. Select one pilot water matrix and site only after a data controller and site operator approve the data and applicable Water Safety Plan limits.
4. Run a retrospective paired sensor/lab evaluation, then a prospective shadow-mode pilot; do not make public water-safety claims from the prototype.

## Sources

1. National Environmental Agency of Georgia. (2025-09-18). *September 18 is World Water Monitoring Day*. https://nea.gov.ge/En/News/2335
2. National Environmental Agency of Georgia. (2026-07-13). *According to laboratory studies conducted by the agency so far, the quality of the Black Sea water along the entire perimeter of the Georgian coast is within the norm*. https://nea.gov.ge/En/News/2417
3. United Water Supply Company of Georgia. (undated; accessed 2026-11-26). *Customer information — water quality control*. https://water.gov.ge/customer-info
4. National Environmental Agency of Georgia. (undated; accessed 2026-11-26). *Water resources*. https://nea.gov.ge/En/popular/6
