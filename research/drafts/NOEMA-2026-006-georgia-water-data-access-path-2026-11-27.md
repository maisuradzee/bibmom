# NOEMA-2026-006 — Georgia groundwater data access: statutory route and registry limits

- **ID:** NOEMA-2026-006
- **Status:** draft
- **Date:** 2026-11-27
- **Scope:** Georgia groundwater monitoring, drinking-water control, public-data access and privacy
- **Related work:** [Georgia water-data access update](NOEMA-2026-006-georgia-water-data-access-update-2026-11-27.md)

## Research question

Which lawful, source-specific routes can AquaSignal use to request Georgian groundwater observations and drinking-water compliance evidence, and what does the new well-registration regime actually cover?

## Executive finding

The legal access picture is more actionable than a simple statement that no public sample-level API has been found. Georgia's Water Resources Management Law creates two distinct institutional routes:

1. **National Environmental Agency (NEA):** Article 32(3) assigns state water monitoring to NEA and says it provides quantitative and qualitative observation data to interested parties on request.
2. **National Food Agency (NFA):** Article 31(3) assigns the state control of drinking-water quality and consumer information about drinking-water quality to NFA.

These provisions identify competent request recipients. They do **not** establish that a public API exists, that every underlying record must be released in raw form, that reuse is unrestricted, or that a particular response time or data format is guaranteed. Groundwater/environmental monitoring and potable-network compliance must therefore be requested and stored as separate datasets.

Government Resolution No.424 creates a prospective well-registration source, but it is not a complete monitoring feed: its scope is limited, its passport contains personal data, and sample/laboratory results are attached only when such testing has occurred.

## FACT — primary-source evidence

### 1. NEA observation-data request route

Article 32(1)–(3) of the Law of Georgia on Water Resources Management defines the state water-monitoring system, assigns its operation to NEA, and states that NEA provides quantitative and qualitative observation data to interested parties on request. It also describes regular hydrological forecasts/warnings and information about water-body pollution.

**Boundary:** this is a statutory route to request monitoring observations. The provision alone does not prove an open API, machine-readable exports, public reuse rights, unrestricted access to personal/operational information, or a guaranteed response deadline.

### 2. Drinking-water control is a separate institutional route

Article 31(3) states that NFA carries out state control of drinking-water quality and provides consumers with information about drinking-water quality.

**Boundary:** a request for potable-network compliance records, sampling denominators or corrective-action summaries should be addressed separately to NFA. It should not be treated as a request for NEA's environmental groundwater station observations.

### 3. Resolution No.424 — prospective well registry, not a universal well census

Government Resolution No.424 was adopted on 31 August 2026 and entered into force on 1 September 2026.

The primary regulation states that it applies to wells deeper than 20 metres drilled to extract fresh drinking groundwater. It excludes mineral, thermal and therapeutic/balneological groundwater and wells drilled before the regulation entered into force. NEA's implementation notice additionally states that household wells in residential plots are excluded whether built before or after 1 September 2026. The household-well exclusion is attributed to the NEA notice; it is not silently inferred from the shorter scope clause in the regulation.

The regulation requires the driller to submit the well passport within 15 working days after drilling is completed. NEA must create and periodically update a hydrogeological database. The passport can contain:
- municipality, settlement, address and well coordinates;
- cadastral code, where available;
- well-owner and drilling-contractor identity/contact fields;
- drilling dates and technical/geological characteristics;
- field sampling results and laboratory-analysis attachments, **if samples were taken and results exist**.

The owner signs the passport to confirm personal-data accuracy and consent to sharing the personal and technical information with NEA for the stated database/reporting purposes. The owner may request information about monitoring and laboratory results where such results exist.

**Interpretation boundary:** registration does not mean every well is sampled. The new register is prospective and incomplete by legal design: it excludes pre-commencement wells and, according to NEA's notice, household wells. It must not be presented as a census of all Georgian wells, a live water-quality feed, or proof that a well's water is potable. Owner identity, personal numbers, contact details and precise private-well locations must never be copied into the public NOEMA repository.

### 4. NEA122 spatial catalogue record

MEPA's GIS catalogue lists NEA122, “Groundwater monitoring”, as a public/free point-geometry layer, with catalogue date 6 March 2026. The row lists SQL SDE/local-computer storage and no portal placement URL. This establishes a catalogue metadata record, not that the point features can currently be downloaded or reused under an open licence.

A station layer is not a sample-result time series. It must not be joined to analytical observations until stable station identifiers, coordinate reference system, water matrix and provenance are verified.

### 5. The 2021–2025 report archive remains an uninspected source lead

NEA's 26 November 2026 announcement links a RAR archive for its 2021–2025 groundwater monitoring report and nitrate-risk field methodology. The announcement confirms that the report and methodology were prepared. The archive's internal files, table granularity, data dictionary and reuse conditions have not been independently inspected in this update. No archive contents are inferred.

## Evidence labels

### FACT
- The Water Resources Management Law assigns state water monitoring to NEA and provides for quantitative/qualitative observation data to be supplied to interested parties on request (Article 32(3)).
- The same law assigns state drinking-water quality control and consumer information to NFA (Article 31(3)).
- Resolution No.424 applies to fresh drinking-groundwater extraction wells deeper than 20 m and excludes wells drilled before 1 September 2026; NEA's 1 September notice separately states the household-well exclusion.
- The regulation requires a well passport within 15 working days after drilling completion and allows field/laboratory results to be attached where available.
- The passport schema includes personal/contact fields and well coordinates.
- MEPA's catalogue row labels NEA122 public/free but lists SQL SDE/local storage and no portal placement URL.

### INFERENCE
- AquaSignal has a defensible next step: submit separately scoped, privacy-reviewed data requests to NEA and NFA rather than assuming the absence of a public API means no lawful access route exists.
- The new registry may become a prospective metadata source for a subset of newly drilled wells, but it cannot replace historical monitoring observations or potable-network compliance data.
- A registry entry without a sample, method, unit, laboratory and collection timestamp cannot support a water-quality classification.

### HYPOTHESIS
If NEA can provide permissioned, provenance-rich groundwater observations and NFA can provide separately defined potable-compliance aggregates with denominators, AquaSignal could test whether source-specific early-warning rules improve operator review time without confusing environmental monitoring with drinking-water safety.

### UNTESTED IDEA
Prepare two separate request specifications:
- NEA: 2021–2025 groundwater report contents, historical groundwater observations/bulletins, NEA122 layer export and data dictionary, sampling methods, units, QA/QC, revisions, publication lag and reuse terms.
- NFA: de-identified potable-water sample counts and non-compliance numerators/denominators, sampling frame, system/geographic strata, collection dates, methods, follow-up actions and publication/reuse conditions.

No request was sent in this cycle. Any future transfer must be reviewed for lawful basis, data minimisation and explicit reuse terms before ingestion.

## Proposed data contract before ingestion

For any authorised observation, require at least:
- source agency and source-record identifier;
- water matrix and sampling-point type;
- station/sample identifier and authorised spatial precision;
- collection timestamp and publication timestamp;
- analyte, result, unit and analytical method;
- LOD/LOQ where relevant;
- laboratory and accreditation scope;
- QA/QC and revision/correction status;
- applicable standard and the exact sampling point to which it applies;
- reuse permission and source-document provenance.

Reject or quarantine records that lack mandatory provenance. Do not infer drinking-water compliance from environmental groundwater or surface-water measurements.

## Reproducibility and limitations

This is a documentary legal/source review, not a reproduced data analysis. No sample-level observations, well-owner records, private coordinates, personal identifiers or laboratory exports were downloaded or added. No legal opinion is offered. The RAR archive and NEA122 feature payload remain uninspected; the statutory request route does not guarantee access or reuse.

## Conclusion

AquaSignal should move from a generic “data unavailable” blocker to a **two-authority request plan**: NEA for environmental monitoring observations under Article 32(3), and NFA for drinking-water state-control information under Article 31(3). Treat Resolution No.424 as a narrow prospective registry with personal-data safeguards, not as a substitute for water-quality monitoring.

## Sources

1. **Law of Georgia on Water Resources Management**, 30 June 2023, consolidated text, Articles 31–34 and 42 (relevant provisions entered into force 1 September 2026). Legislative Herald of Georgia. https://www.matsne.gov.ge/ka/document/download/5846594/3/ge/pdf
2. **Government Resolution No.424**, 31 August 2026, “Rules for Accounting Wells for the Extraction of Fresh Drinking Groundwater”, especially Articles 1–7 and the well passport annex. https://matsne.gov.ge/ka/document/view/6991245
3. **NEA**, 1 September 2026, “A new regulation on state registration of fresh drinking groundwater wells entered into force”. https://nea.gov.ge/%3B/News/2430
4. **NEA**, 26 November 2026, 2021–2025 groundwater monitoring report and nitrate-risk field-methodology announcement. https://nea.gov.ge/ajs/News/3461
5. **MEPA GIS Portal**, NEA122 “Groundwater monitoring” catalogue row, catalogue date 6 March 2026. https://portal.mepa.gov.ge/En/User/data?Links-sort=ResponsiblePerson-asc

## Change history

- 2026-11-27: Added the statutory NEA/NFA request-route distinction, the prospective registry scope and privacy boundary, and a source-specific data-request specification. No data request or ingestion was performed.
