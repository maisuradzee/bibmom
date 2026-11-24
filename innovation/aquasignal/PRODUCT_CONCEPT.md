# AquaSignal — event-triggered drinking-water safety assurance

> Working name. Product concept and engineering hypothesis; not a certified instrument, validated public-health intervention, or demonstrated patentable invention.

- **NOEMA Innovation ID:** NOEMA-INNOVATION-001
- **Version:** 0.1
- **Date:** 2026-11-25
- **Stage:** concept + software proof of concept
- **Target users:** small/community water utilities, rural water committees, schools and health facilities with local water systems
- **Primary problem:** contamination or treatment failures can occur between periodic tests; small operators may lack continuous monitoring, timely confirmatory sampling, and a trustworthy route from sensor anomaly to public action.

## 1. The human problem

WHO and UNICEF reported in August 2025 that 2.1 billion people lacked safely managed drinking-water services. WHO's November 2026 fact sheet reports that at least 1.7 billion people used a drinking-water source contaminated with faeces in 2022 and estimates about 505,000 diarrhoeal deaths annually from microbiologically contaminated drinking water.

The problem this product targets is narrower and actionable: **small water systems often need an affordable way to notice operational changes between scheduled microbiological tests, decide when to collect a new sample, preserve trustworthy sample evidence, and communicate the result without overstating what was tested.**

## 2. What already exists — and what AquaSignal will not copy

Existing field-testing products demonstrate that portable digital microbial testing is possible. WaterScope, for example, describes a portable E. coli testing workflow with an early relative-risk result and a later quantitative result, image-based colony counting, and digital result sharing. WHO guidance recommends operational monitoring using parameters such as turbidity, pH, disinfectant residual, conductivity, pressure, and other site-relevant indicators.

Low-cost sensors and digital testing are therefore not a new discovery by themselves. A review of low-cost IoT sensors identifies reliability, comparability, calibration, and field validation as unresolved issues. Research also stresses that no single operational parameter can detect every contaminant.

**AquaSignal is not a new E. coli assay and does not attempt to replace accredited laboratories, WHO guidance, national standards, or existing validated field kits.** Its product hypothesis is the missing operational bridge between:
1. continuous/regular observation of a water system;
2. a transparent rule for deciding when a change deserves investigation;
3. correctly collected, traceable confirmatory samples;
4. a responsible person's documented response; and
5. a cautious, time-bounded message to affected users.

The concept must be compared against WaterScope and other monitoring networks before any claim of technical or patent novelty. WaterScope's published system already digitises test results and shares them through a dashboard; AquaSignal's potential differentiation is event-triggered, multi-point operational surveillance and the chain from anomaly to sampling, response, and public communication.

## 3. Proposed product

**AquaSignal is an event-triggered water-safety assurance network for small water supplies.**

It combines four cooperating parts:

### A. AquaNode — operational observation

A rugged edge device installed at selected points in a supply system. Depending on the site's water source and treatment process, a node can record selected parameters such as:
- turbidity;
- disinfectant residual (where disinfection is used);
- pressure and flow;
- conductivity;
- pH and temperature.

The initial pilot must use sensors that can be calibrated and maintained locally. Not every parameter belongs at every site. Sensor selection must follow a water-safety plan and local risk assessment. A failed, uncalibrated, or missing sensor must be marked unavailable, not silently treated as a normal reading.

### B. AquaCue — transparent event detection

A small edge/cloud service compares measurements with:
- approved operational limits entered by the responsible water operator or authority;
- a site-specific baseline collected during a verified stable period;
- known operational events such as maintenance, rainfall, pressure loss, treatment interruption, or source change.

AquaCue initially uses interpretable statistical rules (median, median absolute deviation, rate-of-change and explicit operator-set limits), not an opaque AI health classifier.

An event creates a task such as: inspect the source/tank, check disinfection, verify sensor calibration, and collect a confirmatory sample using an approved method. It does **not** declare that pathogens are present merely because a proxy sensor changed.

### C. AquaProof — sample provenance

Each follow-up sample receives a unique sample ID/QR label and a tamper-evident record:
- supply and sampling-point ID;
- date/time and collector;
- sampling protocol and method;
- sensor readings and event that triggered the sample;
- equipment calibration/quality-control status;
- transport and holding conditions where required;
- laboratory or validated field-test result, including method and reporting units;
- reviewer and corrective action.

The system should integrate with existing approved field kits and laboratories rather than inventing an unvalidated microbiological assay. The first MVP uses a guided manual sampling workflow. Automatic sampling hardware is deferred until contamination control, sterile sampling, preservation, and maintenance can be proven.

### D. AquaRelay — response and communication

AquaRelay gives the operator, laboratory, and community a shared incident timeline. It supports offline-first data capture and later synchronisation; SMS or other low-bandwidth alerts can be added after the pilot.

The public status vocabulary is deliberately cautious:
- **Routine monitoring recorded** — not a declaration of safety.
- **Operational deviation — inspection/sample requested.**
- **Sample collected — result pending.**
- **A result was reported for this sample** — with method, location, time and tested parameter.
- **Authority-issued advisory active/resolved** — only when the responsible authority has issued or cleared it.

A negative result must be worded narrowly, for example: “No E. coli detected in this tested 100 mL sample using method X at time Y.” The product must never convert “no sensor anomaly” or one negative sample into a blanket “water is safe” badge.

## 4. The core innovation hypothesis

The candidate innovation is the **event-to-evidence loop**:

1. A site-specific sensor baseline notices a meaningful operational change.
2. The system opens a human inspection and sampling task with the reason attached.
3. A sample is linked to the triggering event and its chain of custody.
4. A validated test or competent laboratory supplies the microbiological/chemical result.
5. A responsible operator or authority records the response.
6. The system learns the site's normal operating range only from quality-controlled records; it does not learn “safety” from unverified data.

This could reduce the time between an operational change and a confirmatory check, while making results more traceable. It is a testable hypothesis, not a demonstrated health impact.

## 5. Users and roles

| Role | Need | AquaSignal function |
|---|---|---|
| Community water operator | Know when to inspect or sample | Node status, event queue, maintenance checklist |
| Field sampler | Collect a valid sample | Guided protocol, sample ID, custody record |
| Laboratory | Receive interpretable metadata | Sample manifest and result upload |
| Local authority | Review incidents and decide response | Event timeline, audit trail, advisory record |
| Resident | Understand what is known and unknown | Plain-language, time-stamped status and official notices |

## 6. Initial prototype scope

The first software prototype is deliberately small:
- ingest a sensor packet;
- compare each channel against a site-specific robust baseline;
- return a transparent REVIEW_REQUIRED or NO_ANOMALY_DETECTED outcome;
- always return water_safety_status = NOT_ESTABLISHED;
- reject missing/non-finite values and insufficient baseline data;
- create no autonomous public-health or treatment decision.

The current Python proof of concept lives in:
- innovation/aquasignal/prototype/anomaly_engine.py
- innovation/aquasignal/prototype/test_anomaly_engine.py

Its test suite covers stable data, an anomalous reading, an insufficient baseline, missing sensor packets, non-finite values, and zero-variance baselines. Passing software tests validates only the code paths; it does not validate sensor accuracy or water safety.

## 7. Pilot plan

**Pilot unit:** one small water supply with the permission of its operator and relevant public-health/water authority. No real deployment should begin until local standards, sampling protocols, and responsibilities are agreed.

**Phase 1 — problem discovery**
- interview operators, samplers, laboratories and residents;
- map the existing monitoring timetable and incident response chain;
- identify source-specific hazards and relevant local regulatory limits;
- document connectivity, electricity, calibration and consumables constraints.

**Phase 2 — bench prototype**
- assemble one sensor node using calibrated reference instruments;
- collect a stable baseline under supervised conditions;
- replay synthetic and controlled sensor deviations;
- verify that alerts are understandable and never presented as pathogen detection.

**Phase 3 — shadow-mode field pilot**
- run alongside existing official monitoring without controlling treatment or issuing safety advisories;
- compare AquaSignal events against manual inspections, operational logs and approved laboratory results;
- record missed events, false alerts, sensor drift, battery/connectivity failures and operator workload.

**Phase 4 — controlled operational evaluation**
- only after authority review, evaluate whether event-triggered sampling shortens time-to-confirmatory-test and improves incident response;
- keep public notices under the relevant authority's control;
- perform independent comparison and publish negative as well as positive findings.

## 8. Success measures

The pilot should measure:
- time from operational deviation to inspection;
- time from deviation to confirmed sample collection;
- proportion of samples with complete provenance;
- sensor uptime and calibration drift;
- alerts per node-day and proportion judged actionable by operators;
- missed operational events found through independent logs or reference testing;
- laboratory agreement for each tested parameter;
- operator time and cost per verified monitoring point;
- user understanding of the difference between “no anomaly detected” and “verified result.”

Thresholds must be agreed before the pilot using the actual supply and baseline data. No performance number is claimed at concept stage.

## 9. Safety, ethics and failure handling

- Sensor proxies are not microbiological tests.
- Absence of an alert is not evidence of safe water.
- Only a validated method can support a result for the analyte it actually measures.
- A sample represents a place and time; it cannot guarantee every tap or later period.
- The system must not autonomously dose chemicals, open/close valves, or issue public-health advisories in the MVP.
- Authority-approved response plans take priority over software suggestions.
- If connectivity fails, local logging continues and the device visibly reports data age.
- If calibration expires or a sensor fails, the channel becomes UNAVAILABLE.
- Personal data should be minimised; sampling records should primarily identify infrastructure and samples, not household members.
- Cybersecurity and tamper-evidence must be designed before any public network connection.

## 10. Main technical risks

| Risk | Mitigation / test |
|---|---|
| Proxy sensors miss a contaminant | Keep confirmatory tests; never claim universal detection |
| Drift/fouling creates false alerts | Calibration schedule, reference checks, fault flags |
| Site baseline is unrepresentative | Establish with operator and seasonal context; version baselines |
| False reassurance from quiet signals | Permanent “safety not established by sensors” wording |
| Poor sample handling | Guided protocol, custody metadata, operator training |
| Network/power outage | Local buffer, low-power design, visible stale-data state |
| Existing solutions already cover the workflow | Competitive review and operator interviews before hardware scale-up |

## 11. What would prove or disprove the idea?

The idea is worth continuing only if a real pilot shows that AquaSignal:
- catches operational changes that fixed-interval sampling would otherwise notice later;
- increases the proportion of actionable, properly collected samples;
- reduces incident-to-confirmation time or response confusion;
- operates at a cost and maintenance burden small water operators can sustain.

The idea should be redesigned or stopped if sensor signals do not reliably help trigger useful tests, if false alarms overwhelm operators, if field maintenance costs exceed the benefit, or if an existing product already provides the same end-to-end service more effectively.

## 12. Research and design references

1. WHO/UNICEF, “1 in 4 people globally still lack access to safe drinking water,” 26 August 2025. https://www.who.int/news/item/26-08-2025-1-in-4-people-globally-still-lack-access-to-safe-drinking-water---who--unicef
2. WHO, “Drinking-water,” 19 November 2026. https://www.who.int/news-room/fact-sheets/detail/Drinking-water
3. WHO, “Guidelines for drinking-water quality: small water supplies,” 2024. Operational monitoring, surveillance and validated field testing. https://iris.who.int/bitstream/handle/10665/375822/9789240088740-eng.pdf
4. WHO, “Guidelines for drinking-water quality,” fourth edition incorporating third addenda, 2026. Operational monitoring parameter examples. https://cdn.who.int/media/docs/default-source/wash-documents/water-safety-and-quality/dwq-guidelines-4/gdwq_4ed_with_third-addenda_water-safety-plans.pdf
5. Camargo et al., “Low-Cost Water Quality Sensors for IoT: A Systematic Review,” Sensors, 2023, 23(9), 4424. https://doi.org/10.3390/s23094424
6. “Contaminations in water distribution systems: a critical review of detection and response methods,” AQUA, 2024. https://doi.org/10.2166/aqua.2024.125
7. “Expanding access to water quality monitoring with the open-source WaterScope testing platform,” npj Clean Water, 23 July 2024. https://www.nature.com/articles/s41545-024-00357-y
8. WaterScope, “WaterScope Portable Kit — Basic,” current public product page, accessed 25 November 2026. https://waterscope.org/product/waterscope-portable-kit-basic/

## 13. Current conclusion

AquaSignal is a plausible, human-centred product direction with a defined problem and a technically testable architecture. It is **not yet proven novel**, not certified, and not field-validated. Its advantage must come from making the entire event-to-evidence-to-response process reliable and affordable for small water systems, not from claiming that inexpensive sensors can certify drinking water.

The next decision gate is a structured prior-art/competitor review and interviews with a small water supplier, a field sampler and a laboratory. Only after that should a physical sensor node be built.
